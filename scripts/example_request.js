// 示例脚本：浏览器内 API 请求
//
// 用于 browser_api 模板
// 必须返回 JSON 对象

(async () => {
  // 使用 window.request 发送 HTTP 请求
  // window.request 由 scripts/request.js 自动注入

  const result = await window.request('https://httpbin.org/json', {
    method: 'GET',
    headers: {
      'Accept': 'application/json'
    },
    timeout: 10000  // 超时（毫秒）
  });

  // result 格式：{ status: number, data: object|string }
  console.log('HTTP 状态码:', result.status);
  console.log('响应数据:', result.data);

  // 必须返回 JSON 对象
  return {
    status: result.status,
    timestamp: new Date().toISOString(),
    data: result.data
  };
})();

// 其他示例：

// POST 请求
// const result = await window.request('https://httpbin.org/post', {
//   method: 'POST',
//   headers: {
//     'Content-Type': 'application/json'
//   },
//   body: {
//     key: 'value',
//     number: 123
//   }
// });

// 访问页面 DOM
// const title = document.querySelector('h1').textContent;
// return { title, ...result.data };

// 错误处理
// try {
//   const result = await window.request('https://example.com/api');
//   return result.data;
// } catch (error) {
//   return { error: error.message };
// }
