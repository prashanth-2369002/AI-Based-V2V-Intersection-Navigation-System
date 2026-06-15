"""
Communication module for V2V and V2I message exchange
Simulates message transmission, delays, and packet loss
"""

import time
import random
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum

import config


class MessageType(Enum):
    """Types of messages exchanged in the system"""
    VEHICLE_INFO = "vehicle_info"
    PRIORITY_ASSIGNMENT = "priority_assignment"
    COLLISION_WARNING = "collision_warning"
    TRAJECTORY_CORRECTION = "trajectory_correction"
    ACK = "acknowledge"


@dataclass
class Message:
    """Represents a message exchanged between vehicles and RSU"""
    sender_id: str
    receiver_id: str
    message_type: MessageType
    timestamp: float
    payload: Dict
    sequence_number: int
    priority: int = 0

    def to_dict(self):
        """Convert message to dictionary"""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        return data

    def __repr__(self):
        return (f"Message(from={self.sender_id}, to={self.receiver_id}, "
                f"type={self.message_type.value}, time={self.timestamp:.2f})")


class CommunicationChannel:
    """Simulates a wireless communication channel with delay and packet loss"""

    def __init__(self, name: str, range_meters: float, delay_ms: float = 0):
        self.name = name
        self.range_meters = range_meters
        self.delay_ms = delay_ms
        self.message_queue: List[tuple] = []  # (delivery_time, message)
        self.sent_messages: List[Message] = []
        self.received_messages: List[Message] = []
        self.delivered_by_receiver: Dict[str, int] = {}
        self.misrouted_deliveries = 0  # messages handed to the wrong recipient (must stay 0)

    def send_message(self, message: Message, current_time: float, distance: float = 0) -> bool:
        """
        Send a message through the channel
        
        Args:
            message: Message to send
            current_time: Current simulation time
            distance: Distance between sender and receiver
            
        Returns:
            bool: True if message was sent successfully, False if lost
        """
        # Check if within range
        if distance > self.range_meters:
            return False

        # Simulate packet loss
        if random.random() < config.MESSAGE_LOSS_RATE:
            return False

        # Add delay
        delay_factor = (distance / self.range_meters) if self.range_meters > 0 else 0
        actual_delay = self.delay_ms * (1 + delay_factor * 0.5)
        delivery_time = current_time + actual_delay / 1000.0

        self.message_queue.append((delivery_time, message))
        self.sent_messages.append(message)
        return True

    def get_messages_for(self, receiver_id: str, current_time: float) -> List[Message]:
        """
        Deliver messages addressed to a specific recipient.

        Only messages that are both due (delivery_time <= current_time) AND
        addressed to receiver_id are removed from the queue. Messages for
        other recipients stay queued until their own recipient polls, so one
        reader can no longer consume or destroy another recipient's mail.
        """
        delivered = []
        remaining = []

        for delivery_time, message in self.message_queue:
            if delivery_time <= current_time and message.receiver_id == receiver_id:
                self.received_messages.append(message)
                delivered.append(message)
            else:
                remaining.append((delivery_time, message))

        self.message_queue = remaining

        # Unit-style validation: everything handed out must belong to the caller
        for message in delivered:
            if message.receiver_id != receiver_id:
                self.misrouted_deliveries += 1
                print(f"[VALIDATION FAIL] {self.name}: message for "
                      f"{message.receiver_id} delivered to {receiver_id}")

        if delivered:
            self.delivered_by_receiver[receiver_id] = (
                self.delivered_by_receiver.get(receiver_id, 0) + len(delivered)
            )

        return delivered

    def get_statistics(self) -> Dict:
        """Get communication channel statistics"""
        total_sent = len(self.sent_messages)
        total_received = len(self.received_messages)
        loss_rate = (1 - total_received / total_sent) if total_sent > 0 else 0

        return {
            'channel_name': self.name,
            'total_messages_sent': total_sent,
            'total_messages_received': total_received,
            'message_loss_rate': loss_rate,
            'pending_messages': len(self.message_queue),
            'delivered_by_receiver': dict(self.delivered_by_receiver),
            'misrouted_deliveries': self.misrouted_deliveries,
        }


class V2VCommunication:
    """Manages Vehicle-to-Vehicle communication"""

    def __init__(self):
        self.channel = CommunicationChannel(
            name="V2V Channel",
            range_meters=config.V2V_RANGE,
            delay_ms=config.COMMUNICATION_DELAY_MS
        )
        self.vehicle_registry: Dict[str, Dict] = {}

    def register_vehicle(self, vehicle_id: str, position: tuple) -> None:
        """Register a vehicle in the V2V network"""
        self.vehicle_registry[vehicle_id] = {
            'last_position': position,
            'last_update': 0,
        }

    def broadcast_vehicle_info(self, vehicle_id: str, vehicle_data: Dict,
                              current_time: float) -> Dict[str, bool]:
        """
        Broadcast vehicle information to all other vehicles
        
        Returns:
            Dict mapping receiver_id to success status
        """
        results = {}
        sender_pos = vehicle_data.get('position', (0, 0))

        for other_id in self.vehicle_registry:
            if other_id == vehicle_id:
                continue

            receiver_pos = self.vehicle_registry[other_id]['last_position']
            distance = self._calculate_distance(sender_pos, receiver_pos)

            message = Message(
                sender_id=vehicle_id,
                receiver_id=other_id,
                message_type=MessageType.VEHICLE_INFO,
                timestamp=current_time,
                payload=vehicle_data,
                sequence_number=0,
                priority=1
            )

            results[other_id] = self.channel.send_message(
                message, current_time, distance
            )

        return results

    def get_received_messages(self, vehicle_id: str, current_time: float) -> List[Message]:
        """Get messages received by a specific vehicle"""
        return self.channel.get_messages_for(vehicle_id, current_time)

    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate Euclidean distance between two positions"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

    def get_statistics(self) -> Dict:
        """Get V2V communication statistics"""
        return self.channel.get_statistics()


class V2ICommunication:
    """Manages Vehicle-to-Infrastructure communication via RSU"""

    def __init__(self, rsu_position: tuple):
        self.rsu_position = rsu_position
        self.channel = CommunicationChannel(
            name="V2I Channel",
            range_meters=config.V2I_RANGE,
            delay_ms=config.COMMUNICATION_DELAY_MS
        )
        self.vehicle_registry: Dict[str, Dict] = {}

    def register_vehicle(self, vehicle_id: str) -> None:
        """Register a vehicle in the V2I network"""
        self.vehicle_registry[vehicle_id] = {
            'last_info': None,
            'priority': None,
            'status': 'waiting',
        }

    def send_vehicle_info_to_rsu(self, vehicle_id: str, vehicle_data: Dict,
                                 current_time: float) -> bool:
        """Send vehicle information to RSU"""
        distance = self._calculate_distance(vehicle_data['position'], self.rsu_position)

        message = Message(
            sender_id=vehicle_id,
            receiver_id="RSU",
            message_type=MessageType.VEHICLE_INFO,
            timestamp=current_time,
            payload=vehicle_data,
            sequence_number=0,
            priority=1
        )

        success = self.channel.send_message(message, current_time, distance)
        if success:
            self.vehicle_registry[vehicle_id]['last_info'] = vehicle_data
        return success

    def get_rsu_messages(self, current_time: float) -> List[Message]:
        """Get messages addressed to the RSU only (vehicle-bound mail stays queued)"""
        return self.channel.get_messages_for("RSU", current_time)

    def get_vehicle_messages(self, vehicle_id: str, current_time: float) -> List[Message]:
        """Get messages addressed to a specific vehicle"""
        return self.channel.get_messages_for(vehicle_id, current_time)

    def send_priority_decision(self, vehicle_id: str, priority_level: int,
                              current_time: float) -> bool:
        """Send priority decision to vehicle"""
        vehicle_pos = self.vehicle_registry.get(vehicle_id, {}).get('last_info', {})
        if not vehicle_pos or 'position' not in vehicle_pos:
            # If no prior position info, use default near intersection
            vehicle_pos = config.INTERSECTION_CENTER
        elif isinstance(vehicle_pos, dict) and 'position' in vehicle_pos:
            vehicle_pos = vehicle_pos['position']

        distance = self._calculate_distance(vehicle_pos, self.rsu_position)

        message = Message(
            sender_id="RSU",
            receiver_id=vehicle_id,
            message_type=MessageType.PRIORITY_ASSIGNMENT,
            timestamp=current_time,
            payload={'priority': priority_level},
            sequence_number=0,
            priority=2
        )

        success = self.channel.send_message(message, current_time, distance)
        if success:
            self.vehicle_registry[vehicle_id]['priority'] = priority_level
        return success

    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate Euclidean distance between two positions"""
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5

    def get_statistics(self) -> Dict:
        """Get V2I communication statistics"""
        return self.channel.get_statistics()
