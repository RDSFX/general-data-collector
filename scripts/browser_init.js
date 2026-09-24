/**
 * 浏览器初始化脚本
 *
 * 通过 Page.add_init_script 注入到文档环境
 * 使 navigator.webdriver 读取为 undefined
 *
 * 注意：
 * - 本脚本仅在特定 Page 的所有导航、刷新和子 frame 生效
 * - 不做 context 级注册，不影响其他 Tab
 * - 不承诺规避其他自动化检测特征
 */

// 修改 Navigator.prototype.webdriver 的 getter
Object.defineProperty(Navigator.prototype, 'webdriver', {
  get: function() {
    return undefined;
  },
  configurable: true,
  enumerable: true
});
