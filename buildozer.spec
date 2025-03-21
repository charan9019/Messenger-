[app]
title = ChatApp
package.name = chatapp
package.domain = com.example
source.include_exts = py,png,jpg,kv,atlas
requirements = python3,kivy,kivymd,firebase-admin
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk_api = 21
android.gradle_dependencies = "com.google.firebase:firebase-database:20.1.0"
android.meta_data = "com.google.firebase.database"
android.presplash_color = "#FFFFFF"
p4a.branch = master
android.ndk = 23b

[buildozer]
log_level = 2
warn_on_root = 1