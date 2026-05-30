[app]

title = Expense Tracker

package.name = expensetracker
package.domain = org.avsk

source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas

version = 0.1

requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow

orientation = portrait

fullscreen = 0

android.api = 33
android.minapi = 21

android.accept_sdk_license = True

android.permissions = INTERNET

presplash.color = #FFFFFF

icon.filename =

[buildozer]

log_level = 2

warn_on_root = 1
