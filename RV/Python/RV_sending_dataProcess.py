import json
from subprocess import Popen, PIPE


inputData = {"shot01": ["animation", "render", "comp"], "shot02": ["render"], "shot03": ["comp"]}
inputData = json.dumps(inputData).encode()
# print(inputData)

command = ["C:/Program Files/Shotgun/RV-7.8.0/bin/rvpush.exe", "-tag", "target", "merge", "d:/Projects/knp/FAU/plane_damage/out/v22_cam_sh/v20_cam_sh.####.exr"]

process = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
out, err = process.communicate(input=inputData)
# print("OUT = ", out.decode('utf-8').strip().replace("\n", ""))
err = err.decode('utf-8').strip().replace("\n", "")

# err ='WARNING: RESALT:: {"v22_cam_sh": "c:\\users\\zaem0\\appdata\\local\\temp\\TiToP\\RV\\c5fdb940-c595-11ea-94be-509a4cc4614d\\v22_cam_sh.#.jpg"}'

# print(err)
# print("=======")
if "RESALT::" in err:
	start = err.find("::")
	end = err.find("}")
	res = err[start+2: end+1].strip()
	res = json.loads(res)


print(res)
print(type(res))	# print(err)



# import json

# stdin = sys.stdin
# inputData = stdin.__dict__.get('_handle').readline()
# inputData = json.loads(inputData)
# print(inputData)
# print(type(inputData))



