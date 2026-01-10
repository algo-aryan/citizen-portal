package com.citizenportal.app;

import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.JavascriptInterface;
import android.webkit.URLUtil;
import android.webkit.WebView;
import android.widget.Toast;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    
    private String sharedImageUri = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Setup the Bridge Interface
        WebView webView = this.getBridge().getWebView();
        webView.addJavascriptInterface(new WebAppInterface(), "AndroidBridge");
        
        handleIncomingShare(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        handleIncomingShare(intent);
    }

    private void handleIncomingShare(Intent intent) {
        if (Intent.ACTION_SEND.equals(intent.getAction()) && intent.getType() != null) {
            if (intent.getType().startsWith("image/")) {
                Uri imageUri = (Uri) intent.getParcelableExtra(Intent.EXTRA_STREAM);
                if (imageUri != null) {
                    sharedImageUri = imageUri.toString();
                    // Redirect immediately to the forensic lab
                    this.getBridge().getWebView().loadUrl("file:///android_asset/public/lab.html");
                }
            }
        }
    }

    // HANDSHAKE INTERFACE: JavaScript calls this to get the URI
    public class WebAppInterface {
        @JavascriptInterface
        public String getPendingImage() {
            String temp = sharedImageUri;
            sharedImageUri = null; // Reset after delivery
            return temp;
        }
    }

    @Override
    public void onStart() {
        super.onStart();
        WebView webView = this.getBridge().getWebView();
        if (webView != null) {
            webView.setDownloadListener(new DownloadListener() {
                @Override
                public void onDownloadStart(String url, String userAgent, String contentDisposition, String mimetype, long contentLength) {
                    try {
                        DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
                        String cookies = CookieManager.getInstance().getCookie(url);
                        request.addRequestHeader("cookie", cookies);
                        request.addRequestHeader("User-Agent", userAgent);
                        request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
                        request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, URLUtil.guessFileName(url, contentDisposition, mimetype));
                        DownloadManager dm = (DownloadManager) getSystemService(Context.DOWNLOAD_SERVICE);
                        dm.enqueue(request);
                        Toast.makeText(getApplicationContext(), "Download Started...", Toast.LENGTH_SHORT).show();
                    } catch (Exception e) {
                        Toast.makeText(getApplicationContext(), "Download Failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
                    }
                }
            });
        }
    }
}