from flask import Flask, request, jsonify
import json
from openai import OpenAI
import office
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/generate": {
        "origins": "http://localhost:5173",
        "methods": ["POST", "OPTIONS"],  # 允许 POST 和预检请求
        "allow_headers": ["Content-Type"]  # 允许 Content-Type 头
    }
})
# 原有的函数保持不变
def split_blocks(data):
    #print("数据中的所有键:", list(data.keys()))  # 调试：打印所有键
    blocks = {}
    block_keys = []

    # 1. 找出所有主标题的索引
    for key in data.keys():
        if key.startswith("title") and key[5:].isdigit() and "-" not in key:
            block_num = int(key[5:])
            block_keys.append(block_num)

    max_block = max(block_keys) if block_keys else 0  # 获取最大块号
    #print("最大块号:", max_block)  # 调试：打印最大块号

    # 2. 动态处理每个块
    for i in range(1, max_block + 1):
        block_key = f"data{i}"
        block_data = {}

        # 添加主标题（值转为列表）
        main_title_key = f"title{i}"
        if main_title_key in data:
            block_data[main_title_key] = [data[main_title_key]]

        # 添加每个子项（值转为列表）
        for j in range(1, 4):  # 子项编号从 1 到 3
            title_key = f"title{i}-{j}"
            data_key = f"data{i}-{j}"

            if title_key in data:
                block_data[title_key] = [data[title_key]]
            if data_key in data:
                block_data[data_key] = [data[data_key]]

        # 如果块中至少有一个有效键，则加入结果
        if block_data:
            blocks[block_key] = block_data

    #print("生成的 blocks:", blocks)  # 调试：打印 blocks 内容
    return blocks

merged_data = {}
for i in range(1, 31):  # 假设最多30页
    merged_data[f"title{i}"] = []
    for j in range(1, 4):
        merged_data[f"title{i}-{j}"] = []
        merged_data[f"data{i}-{j}"] = []

data = {
    "title": "xxxxxx",
    "name": "xxxxxx",
    "title1": "xxxxxx",
    "title1-1": "xxxxxx", "data1-1": "xxxxxx",
    "title1-2": "xxxxxx", "data1-2": "xxxxxx",
    "title1-3": "xxxxxx", "data1-3": "xxxxxx",

    "title2": "xxxxxx",
    "title2-1": "xxxxxx", "data2-1": "xxxxxx",
    "title2-2": "xxxxxx", "data2-2": "xxxxxx",
    "title2-3": "xxxxxx", "data2-3": "xxxxxx",

    "title3": "xxxxxx",
    "title3-1": "xxxxxx", "data3-1": "xxxxxx",
    "title3-2": "xxxxxx", "data3-2": "xxxxxx",
    "title3-3": "xxxxxx", "data3-3": "xxxxxx",

    "title4": "xxxxxx",
    "title4-1": "xxxxxx", "data4-1": "xxxxxx",
    "title4-2": "xxxxxx", "data4-2": "xxxxxx",
    "title4-3": "xxxxxx", "data4-3": "xxxxxx",

    "title5": "xxxxxx",
    "title5-1": "xxxxxx", "data5-1": "xxxxxx",
    "title5-2": "xxxxxx", "data5-2": "xxxxxx",
    "title5-3": "xxxxxx", "data5-3": "xxxxxx",

    "title6": "xxxxxx",
    "title6-1": "xxxxxx", "data6-1": "xxxxxx",
    "title6-2": "xxxxxx", "data6-2": "xxxxxx",
    "title6-3": "xxxxxx", "data6-3": "xxxxxx",

    "title7": "xxxxxx",
    "title7-1": "xxxxxx", "data7-1": "xxxxxx",
    "title7-2": "xxxxxx", "data7-2": "xxxxxx",
    "title7-3": "xxxxxx", "data7-3": "xxxxxx",

    "title8": "xxxxxx",
    "title8-1": "xxxxxx", "data8-1": "xxxxxx",
    "title8-2": "xxxxxx", "data8-2": "xxxxxx",
    "title8-3": "xxxxxx", "data8-3": "xxxxxx",
}

# 设置API密钥
api_key = "**************************************"  # 替换为实际的API密钥

def call_deepseek_api(prompt, num):
    try:
        beg = "以下是8页ppt的格式:"+json.dumps(data)+"请仿照该格式生成"+str(num)+"页ppt内容，其中内容部分，控制在所总结原文内容20%到30%的字数"
        messages = [
            {"role": "system", "content": "你是一个PPT制作专家，你不会放过任何一个技术细节介绍"+beg}
        ]
        # 更新对话历史
        messages.append({"role": "user", "content": prompt})
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        # 发送API请求
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=8192
        )
        # 获取API响应内容
        full_content = ""
        for chunk in response:
            if hasattr(chunk.choices[0].delta, 'content'):
                content = chunk.choices[0].delta.content
                full_content += content
                yield full_content
        #返回完整内容  
        return full_content
    except Exception as e:
        print(f"API调用失败: {str(e)}")

def extract_json_from_text(text):
    # 去除 Markdown 代码块标记
    text = text.replace("```json", "").replace("```", "")
    
    # 提取 JSON 部分
    start_index = text.find("{")
    end_index = text.rfind("}")
    
    if start_index != -1 and end_index != -1 and start_index < end_index:
        json_str = text[start_index:end_index+1]
        return json_str
    else:
        raise ValueError("无法找到有效的JSON部分")

@app.route('/generate', methods=['POST'])
def generate_ppt():
    try:
        data = request.get_json()
        page_count = data.get('pageCount', 5)
        input_content = data.get('inputContent', '')

        if not (1 <= int(page_count) <= 30):
            return jsonify({"error": "页数必须在1-30之间"}), 400
        
        def generate_response():
            try:
                full_content = ""
                for chunk in call_deepseek_api(input_content, page_count):
                    # 直接返回纯文本块（不加 data: 前缀）
                    full_content = chunk
                    yield chunk
                try:
                    formatted_data = json.loads(extract_json_from_text(full_content))
                    result = split_blocks(formatted_data)
                    #print(formatted_data)
                    author = {
                        "title": formatted_data["title"],
                        "name": formatted_data["name"]
                    }
                    ppt = office.open_file("output.pptx", template="ppt初版.pptx")
                    for block_key, block_data in result.items():
                        new_block_data = {}
                        for original_key, value in block_data.items():
                            new_block_data[original_key] = value
                        for key, val in new_block_data.items():
                            merged_data[key].extend(val)
                    
                    ppt.fill(author)
                    ppt.fill(merged_data).save()
                    yield "PPT生成成功\n"
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误位置：行{e.lineno}，列{e.colno}，原因：{e.msg}")
                    yield f"JSON解析失败: {str(e)}\n"
                except KeyError as e:
                    yield f"缺少必要字段: {str(e)}\n"
            except Exception as e:
                yield f"错误：API调用失败 - {str(e)}\n"
        # 设置正确的 Content-Type
        response = app.response_class(generate_response(), mimetype='text/event-stream')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['X-Accel-Buffering'] = 'no'  # 防止 Nginx 缓存
        return response
    except Exception as e:
        print(f"[服务器错误] {str(e)}")
        return jsonify({"error": "服务器内部错误"}), 500

if __name__ == '__main__':
    app.run(debug=True)  # 显式指定端口（可选）
    
