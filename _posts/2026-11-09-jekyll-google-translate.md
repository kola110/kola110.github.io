---
title: "给 Jekyll 博客加多语言翻译：藏起官方下拉框，自己做选择器"
date: 2026-11-09
category: 编程
excerpt: "给 Jekyll 博客接 Google 翻译，藏起官方下拉框自己做选择器，顺手修了它改写选项文字的坑。"
minutes: "约 6 分钟"
---

今天给博客「代码与日子」加了多语言翻译。博客是中文写的，但希望不懂中文的读者也能读。Google 翻译免费、接入也简单，本来以为十分钟就能完事，结果在两个地方卡住了：官方下拉框会把语言名翻译成本地文字，而翻译本身还会反过来改写我自己的选择器。这篇文章记录这两个坑和解决办法。

## 一、官方控件的第一个问题：语言名全变成了中文

Google 翻译的标准用法，是在页面上放一个小部件，初始化时指定源语言和允许的目标语言：

```js
function googleTranslateElementInit() {
  new google.translate.TranslateElement({
    pageLanguage: 'zh-CN',
    includedLanguages: 'en,ja,ko,fr,de,es,ru',
    layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
    autoDisplay: false
  }, 'google_translate_element');
}
```

这样确实能翻译，但它自带的下拉框有个毛病：语言名会按当前页面语言本地化。页面是中文的，下拉框里就全是中文——English 显示成“英语”，日本語显示成“日语”。对一个不懂中文的读者来说，这个选择器本身就看不懂，翻译功能等于摆设。

所以第一步是把官方控件藏起来，自己做选择器。官方小部件只留一个空容器，用 CSS 藏好：

```html
<span id="google_translate_element" class="translate-widget-hidden"></span>
```

选择器则自己写一个 `<select>`，选项直接用各语言自己的文字：中文、English、日本語、한국어、Français、Deutsch、Español、Русский。再给它加上 `notranslate` 类和 `translate="no"` 属性，告诉翻译引擎别碰它。

选了语言之后，要让藏起来的官方控件真正去翻译。做法是找到它生成的 `.goog-te-combo`，改值并触发 change 事件；如果它还没生成，就写 `googtrans` cookie 再刷新页面：

```js
sel.addEventListener('change', function() {
  var lang = sel.value;
  if (!lang || lang === 'zh-CN') {
    document.cookie = 'googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/';
    location.reload();
    return;
  }
  var combo = document.querySelector('.goog-te-combo');
  if (combo) {
    combo.value = lang;
    combo.dispatchEvent(new Event('change'));
  } else {
    document.cookie = 'googtrans=/zh-CN/' + lang + '; path=/';
    location.reload();
  }
});
```

切回中文时清掉 cookie 再刷新，页面就恢复原文。刷新后还会从 `googtrans` cookie 里把选择器的当前值恢复出来，免得每次进页面都显示默认项。

## 二、第二个坑：翻译还会改写选择器本身

做到这里以为完事了，结果一切换语言就发现：选择器里的选项文字也被翻译了——日本語变成了 Japanese，中文变成了 Chinese。明明加了 `notranslate` 类和 `translate="no"`，Google 翻译还是改了 `<option>` 的文字。

这说明靠标记“不要翻译我”拦不住它。换个思路：拦不住就别拦，改了再改回来。把每个选项应有的文字记在一张表里：

```js
var LANG_LABELS = {'zh-CN': '中文', 'en': 'English', 'ja': '日本語',
  'ko': '한국어', 'fr': 'Français', 'de': 'Deutsch',
  'es': 'Español', 'ru': 'Русский'};
```

再用 `MutationObserver` 盯住选择器，一旦发现选项文字被动过，就按表恢复：

```js
function restoreLangLabels() {
  var sel = document.getElementById('lang-select');
  if (!sel) return;
  for (var i = 0; i < sel.options.length; i++) {
    var o = sel.options[i];
    var label = LANG_LABELS[o.value];
    if (label && o.text !== label) o.text = label;
  }
}

var mo = new MutationObserver(function() { restoreLangLabels(); });
mo.observe(sel, {childList: true, subtree: true, characterData: true});
```

监听要同时开 `childList`、`subtree` 和 `characterData`，因为翻译改的是选项的文本节点，不一定动得到元素结构。初始化时先恢复一次，再挂上监听，之后不管翻译什么时候改写，选择器都会自己把名字改回来。

## 三、效果和边界

现在切到 English，首页的标题、导航、文章标题都翻译了，顶部出现 Google 的“已翻译为英语”提示条；切回中文，页面恢复原样。整个过程中，右上角的选择器始终显示各语言自己的文字。

有三点边界要说清楚：

- 这是机器翻译，只适合让读者大致读懂，谈不上准确，更不能代替人工翻译。
- 翻译后的页面没有独立地址，搜索引擎不会收录英文版，分享出去的还是中文原文链接。
- 翻译依赖 Google 的服务，在无法访问 Google 的网络环境下不可用。

如果以后要认真做多语言，正确的做法是给每种语言单独写内容、单独生成页面。Google 翻译只是零成本的过渡方案：不改文章、不改结构，一天就能让全站多出七种语言的“能读版”。

---

**翻译控件本身也要防翻译——做多语言的第一步，是先让语言选择器说自己的母语。**
