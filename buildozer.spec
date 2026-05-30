[app]

title = Expense Tracker

package.name = expensetracker

package.domain = org.avsk

source.dir = .

source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3==3.11.9,kivy,kivymd,sqlite3
orientation = portrait

fullscreen = 0

android.api = 33
android.sdk = 24
android.ndk = 25b
android.accept_sdk_license = True

android.minapi = 21

android.permissions = INTERNET

[buildozer]

log_level = 2

warn_on_root = 1
