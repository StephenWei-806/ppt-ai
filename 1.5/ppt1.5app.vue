<template>
    <div id="app">
      <h1 style="color: #003366;">AI-PPT 1.5</h1>
      <div style="margin-bottom: 20px;">
        <label for="pageCount" style="color: #000000; font-weight: bold;">选择PPT页数 (1 - 10):</label>
        <select 
          id="pageCount" 
          v-model="pageCount" 
          style="border: 1px solid #cccccc; padding: 8px; border-radius: 4px; margin-left: 10px;"
        >
          <option v-for="i in 10" :key="i" :value="i">{{ i }}</option>
        </select>
      </div>
      <div style="margin-bottom: 20px;">
        <label for="inputContent" style="color: #000000; font-weight: bold;">输入内容:</label>
        <textarea 
          id="inputContent" 
          v-model="inputContent" 
          rows="4" 
          cols="50"
          style="border: 1px solid #cccccc; padding: 8px; border-radius: 4px; margin-left: 10px; color: #000000;"
        ></textarea>
      </div>
      <button 
        @click="generatePPT" 
        style="border: 2px solid #000000; background-color: #ffffff; color: #000000; 
               padding: 12px 24px; border-radius: 8px; font-weight: bold; cursor: pointer;"
      >
        生成PPT
      </button>
      <div v-if="responseContent.length > 0" style="margin-top: 30px;">
        <h2>API响应内容:</h2>
        <pre>{{ responseContent }}</pre>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  import axios from 'axios';
  
  // 定义响应式数据
  const pageCount = ref('8'); // 默认选中8页
  const inputContent = ref('请分析2025年的就业趋势'); // 预填内容
  const responseContent = ref('');
  
  const generatePPT = async () => {
    try {
      const res = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pageCount: pageCount.value,
          inputContent: inputContent.value,
        }),
      });
  
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
  
      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let result = '';
  
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        responseContent.value = chunk; // 实时更新响应式变量
      }
    } catch (error) {
      console.error('请求失败:', error);
      responseContent.value = '请求失败，请重试';
    }
  };
  </script>
  
  <style scoped>
  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin-top: 60px;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }
  </style>