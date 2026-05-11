import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        host_api = p.get_host_api_info_by_index(info['hostApi'])['name']
        print(f"[{i}] {info['name']} (API: {host_api})")
