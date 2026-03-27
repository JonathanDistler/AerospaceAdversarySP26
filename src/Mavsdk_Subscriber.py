#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Vector3Stamped, AccelStamped
from datetime import datetime
import csv
import os


class DroneListener(Node):
    def __init__(self):
        super().__init__('drone_listener')

        # Create a log directory
        log_dir = os.path.expanduser('~/drone_logs')
        os.makedirs(log_dir, exist_ok=True)

        # Create timestamped CSV file
        self.filename = os.path.join(
            log_dir,
            f"Mavlink_Drone_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        # Open CSV file in append mode
        self.file = open(self.filename, 'a', newline='')
        self.writer = csv.writer(self.file)

        # Write CSV header
        self.writer.writerow([
            "timestamp",
            "topic",
            "field_1",
            "field_2",
            "field_3"
        ])
        self.file.flush()

        self.get_logger().info(f"Logging all topics to {self.filename}")

        # Create all subscribers
        self.create_subscription(String, 'drone_status', self.status_cb, 10)
        self.create_subscription(NavSatFix, 'drone_gps', self.gps_cb, 10)
        self.create_subscription(Float32, 'drone_battery', self.batt_cb, 10)
        self.create_subscription(Float32, 'drone_altitude', self.alt_cb, 10)
        self.create_subscription(Vector3Stamped, 'drone_angle_vel', self.angle_vel_cb, 10)
        self.create_subscription(Vector3Stamped, 'drone_euler', self.euler_cb, 10)
        self.create_subscription(AccelStamped, 'drone_accel', self.accel_cb, 10)

    # ---------------------------------------------------------------
    # Utility: write one row immediately
    # ---------------------------------------------------------------
    def log_row(self, topic, f1="", f2="", f3=""):
        t = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.writer.writerow([t, topic, f1, f2, f3])
        self.file.flush()  # ensures immediate write to disk

    # ---------------------------------------------------------------
    # Callbacks for each topic
    # ---------------------------------------------------------------
    def status_cb(self, msg):
        self.get_logger().info(f"[STATUS] {msg.data}")
        self.log_row("drone_status", msg.data)

    def gps_cb(self, msg):
        self.get_logger().info(
            f"[GPS] Lat={msg.latitude:.6f}, Lon={msg.longitude:.6f}, Alt={msg.altitude:.1f} m"
        )
        self.log_row("drone_gps", msg.latitude, msg.longitude, msg.altitude)

    def batt_cb(self, msg):
        self.get_logger().info(f"[BATT] {msg.data:.1f}%")
        self.log_row("drone_battery", msg.data)

    def alt_cb(self, msg):
        self.get_logger().info(f"[ALT] {msg.data:.1f} m")
        self.log_row("drone_altitude", msg.data)

    def angle_vel_cb(self, msg):
        v = msg.vector
        self.get_logger().info(
            f"[ANG_VEL] Roll={v.x:.3f}, Pitch={v.y:.3f}, Yaw={v.z:.3f} rad/s"
        )
        self.log_row("drone_angle_vel", v.x, v.y, v.z)

    def euler_cb(self, msg):
        v = msg.vector
        self.get_logger().info(
            f"[EULER] Roll={v.x:.2f}°, Pitch={v.y:.2f}°, Yaw={v.z:.2f}°"
        )
        self.log_row("drone_euler", v.x, v.y, v.z)

    def accel_cb(self, msg):
        a = msg.accel.linear
        self.get_logger().info(
            f"[ACCEL] Fwd={a.x:.2f}, Right={a.y:.2f}, Down={a.z:.2f} m/s²"
        )
        self.log_row("drone_accel", a.x, a.y, a.z)

    # ---------------------------------------------------------------
    # Clean shutdown
    # ---------------------------------------------------------------
    def destroy_node(self):
        self.file.close()
        self.get_logger().info(f" Data saved to {self.filename}")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = DroneListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()


