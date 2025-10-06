import xml.etree.ElementTree as ET
import math

def convert_xar_to_py(xar_file_path, output_py_path, time_scale=4.8):
    tree = ET.parse(xar_file_path)
    root = tree.getroot()

    py_script = []
    py_script.append("import math")
    py_script.append("import threading")
    py_script.append("")
    py_script.append("def execute_motion(motion_proxy):")
    py_script.append("    names = []")
    py_script.append("    times = []")
    py_script.append("    keys = []")

    fps = 25  # Assuming a default frame rate of 25 fps

    for actuator_curve in root.findall(".//ActuatorCurve"):
        actuator_name = actuator_curve.get("actuator")
        py_script.append(f"    names.append(\"{actuator_name}\")")

        time_list = []
        key_list = []

        for key in actuator_curve.findall(".//Key"):
            frame = int(key.get("frame"))
            value = float(key.get("value"))

            time_in_seconds = (frame / fps) * time_scale
            angle_in_radians = math.radians(value)

            time_list.append(time_in_seconds)
            key_list.append(f"[math.radians({value}), [3, -0.25, 0], [3, 0.25, 0]]")

        py_script.append(f"    times.append({time_list})")
        py_script.append(f"    keys.append([{', '.join(key_list)}])")

    py_script.append("    motion_proxy.angleInterpolationBezier(names, times, keys)")

    with open(output_py_path, "w") as py_file:
        py_file.write("\n".join(py_script))

# Example usage:
# convert_xar_to_py("input.xar", "output.py", time_scale=2.0)
convert_xar_to_py("/home/samuel/NAO_TALK/Tai Chi Chuan/box.xar","/home/samuel/NAO_TALK/motions/taichi.py", time_scale=4.5)