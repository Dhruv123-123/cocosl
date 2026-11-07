// Service worker: right-click menus, and (only if the user turns it on) a red badge on look-alike sites.
// Nothing leaves the browser: every check runs on this device.
import { checkPage, badgeFor, menuText } from './lib/site.js';

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({ id: 'check-selection', title: chrome.i18n.getMessage('menuSelection'), contexts: ['selection'] });
    chrome.contextMenus.create({ id: 'check-link', title: chrome.i18n.getMessage('menuLink'), contexts: ['link'] });
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  const text = menuText(info);
  if (!text) return;
  chrome.windows.create({
    url: chrome.runtime.getURL(`popup.html?window=1#m=${encodeURIComponent(text)}`),
    type: 'popup', width: 420, height: 640,
  });
});

async function warningsOn() {
  try {
    const [{ siteWarnings }, allowed] = await Promise.all([
      chrome.storage.local.get('siteWarnings'),
      chrome.permissions.contains({ permissions: ['tabs'] }),
    ]);
    return Boolean(siteWarnings && allowed);
  } catch { return false; }
}

async function updateBadge(tabId, url) {
  if (!url) return;
  const badge = (await warningsOn()) ? badgeFor(checkPage(url).level) : null;
  await chrome.action.setBadgeText({ tabId, text: badge ? badge.text : '' });
  if (badge) {
    await chrome.action.setBadgeBackgroundColor({ tabId, color: badge.color });
    await chrome.action.setTitle({ tabId, title: chrome.i18n.getMessage('badgeTitle') });
  }
}

// tab.url is only present once the user grants the optional "tabs" permission from the popup.
chrome.tabs.onUpdated.addListener((tabId, change, tab) => {
  if (change.url || change.status === 'complete') updateBadge(tabId, tab.url).catch(() => {});
});
