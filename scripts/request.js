/**
 * 浏览器内 HTTP 请求封装
 *
 * 基于 fetch API，用于 browser_api 模板中的 JavaScript 脚本
 * 返回格式：{status: number, data: object|string}
 */

/**
 * 发送 HTTP 请求
 *
 * @param {string} url - 请求 URL
 * @param {object} options - 请求选项
 * @param {string} options.method - HTTP 方法（默认 GET）
 * @param {object} options.headers - 请求头
 * @param {object|string} options.body - 请求体（对象自动序列化为 JSON）
 * @param {number} options.timeout - 超时毫秒数（默认 10000）
 * @returns {Promise<{status: number, data: object|string}>}
 */
async function request(url, options = {}) {
  const {
    method = 'GET',
    headers = {},
    body = null,
    timeout = 10000
  } = options;

  // 构造 fetch 选项
  const fetchOptions = {
    method: method.toUpperCase(),
    headers: { ...headers }
  };

  // 处理请求体
  if (body !== null) {
    if (typeof body === 'object') {
      fetchOptions.body = JSON.stringify(body);
      if (!fetchOptions.headers['Content-Type']) {
        fetchOptions.headers['Content-Type'] = 'application/json';
      }
    } else {
      fetchOptions.body = body;
    }
  }

  // 超时控制
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  fetchOptions.signal = controller.signal;

  try {
    // 发送请求
    const response = await fetch(url, fetchOptions);
    clearTimeout(timeoutId);

    // 获取状态码
    const status = response.status;

    // 解析响应体
    let data;
    const contentType = response.headers.get('Content-Type') || '';

    if (contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    return { status, data };

  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout}ms`);
    }
    throw new Error(`Request failed: ${error.message}`);
  }
}

// 导出（在浏览器环境中挂载到 window）
if (typeof window !== 'undefined') {
  window.request = request;
}
