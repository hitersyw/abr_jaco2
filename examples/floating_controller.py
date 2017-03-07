"""moves jaco to various joint positions and switches to torque
mode and float controller, records joint positions. Test to
quantify gravity compensation improvements"""
import numpy as np
import abr_control
import abr_jaco2
# --- NAME TEST FOR SAVING ---

# ---------- INITIALIZATION ----------
# initialize our robot config for the ur5
robot_config = abr_jaco2.robot_config(
    use_cython=True, hand_attached=True)

ctrlr = abr_control.controllers.floating(robot_config)
ctrlr.control(np.zeros(6), np.zeros(6))

interface = abr_jaco2.interface(robot_config)

interface.connect()
interface.init_position_mode()

# ---------- MAIN BODY ----------
# Move to home position
interface.apply_q(robot_config.init_torque_position)

try:
    # move to read position ii
    t_feedback = interface.get_torque_load()
    torque_load = np.array(t_feedback['torque_load'], dtype="float32")
    t_feedback = interface.get_torque_load()

    interface.init_force_mode()
    while 1:
        # get arm feedback
        feedback = interface.get_feedback()
        q = np.array(feedback['q'])
        dq = np.array(feedback['dq'])
        print('q: ', q)
        print('xyz: ', robot_config.Tx('EE', q=q))
        u = ctrlr.control(q=q, dq=dq)
        interface.send_forces(np.array(u, dtype='float32'))

except Exception as e:
    print(e)

finally:
    interface.init_position_mode()
    interface.apply_q(robot_config.init_torque_position)
    interface.disconnect()
    print('Disconnected')
