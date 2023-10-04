import os
import sys
import json
import base64
import ffmpeg
# 使用正则表达式提取字符串中的数字部分
import re

# 自定义排序函数，提取字符串中的数字作为排序依据
def sort_by_num(s):
    matches = re.findall(r'\d+', s)
    if matches:
        return int(matches[-1])
    else:
        # 如果没有数字，返回一个足够大的数，确保它排在最后
        return float('inf')

def main():
    videoFlag = False
    if len(sys.argv) > 1:
        inputfilename = sys.argv[1]
    else:
        inputfilename = "dev.epicgames.com_Archive [23-09-19 23-32-59].har"
    
    segMax = 0
    f = open(inputfilename,"r",encoding="utf-8")
    jsonData = json.load(f)
    entries = jsonData['log']['entries']
    init_filenames = []
    segment_filenames = []
    for entry in entries:
        request = entry['request']
        response = entry['response']
        if request['method'] != 'GET':
            continue
        # print(request['url'])
        if 'mimeType' in response['content'] and response['content']['mimeType'] == "video/mp4":
            if ".mp4" in request['url'] or ".m4s" in request['url']:
                videoFlag = True
                if "init" in request['url'] or "segment_" in request['url']:
                    url = request['url']                
                    videoName = url.split("/")[-1].split("?")[0]
                    videoBase64Text = response['content']['text']
                    if "segment_" in videoName:
                        segment_filenames.append(videoName)
                        segNum = int(videoName.split("_")[1].split(".")[0]) 
                        if segNum > segMax :
                            segMax = segNum
                    if "init_" in request['url']:
                        init_filenames.append(videoName)
                    videoFileSeg = open('video_'+videoName+'.temp', 'wb', buffering=0)
                    videoFileSeg.write(base64.b64decode(videoBase64Text))
                    videoFileSeg.close()
            # elif "/audio/" in request['url']:
            #     if "init" in request['url'] or "seg_" in request['url']:
            #         url = request['url']                
            #         audioName = url.split("/")[-1].split("?")[0]
            #         audioBase64Text = response['content']['text']    
            #         audioFileSeg = open('audio_'+audioName+'.temp', 'wb', buffering=0)
            #         audioFileSeg.write(base64.b64decode(audioBase64Text))
            #         audioFileSeg.close()

    f.close()

    if videoFlag == False:
        print("No Video Content Detected!")
        return

    # videoTemp = ffmpeg.input("video_init.mp4.temp")

    init_filenames.sort(key=sort_by_num)
    for init_filename in init_filenames:
        initgNum = int(init_filename.split("_")[1].split(".")[0])
        videoFile = open(init_filename, 'wb', buffering=0)
        initVideo = open("video_"+init_filename+".temp", 'rb', buffering=0)
        videoFile.write(initVideo.read())
        initVideo.close()
        
        # 使用列表推导式找出所有包含'segment_n'的元素
        filtered_segment_filenames = [item for item in segment_filenames if 'segment_'+str(initgNum) in item]
        filtered_segment_filenames.sort(key=sort_by_num)
        for segment_filename in filtered_segment_filenames:
            segVideo = open("video_"+segment_filename+".temp", 'rb', buffering=0)
            videoFile.write(segVideo.read())
            segVideo.close()
        videoFile.close()

    # videoFile.close()
    # audioFile.close()

    # try:       
    #     video = ffmpeg.input('video.mp4.temp')
    #     audio = ffmpeg.input('audio.mp4.temp')
    #     output = ffmpeg.output(video, audio, 'output.mp4')
    #     ffmpeg.run(output, overwrite_output=True)
    # except:
    #     print("ffmpeg Not Found!")

    for (dirpath, dirnames, filenames) in os.walk('./'):
        for filename in filenames:
            if '.mp4.temp' in filename:
                os.remove(filename)
            if '.m4s.temp' in filename:
                os.remove(filename)


if __name__ == '__main__':
    main()