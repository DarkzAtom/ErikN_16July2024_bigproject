
    var config = {
        mode: "fixed_servers",
        rules: {
            singleProxy: {
                scheme: "http",
                host: "62.164.231.149",
                port: parseInt(9461)
            },
            bypassList: ["localhost"]
        }
    };

    chrome.proxy.settings.set({ value: config, scope: "regular" }, function () {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "ramxcgif",
                password: "vk9ai0q1t67y"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        { urls: ["<all_urls>"] },
        ['blocking']
    );
    