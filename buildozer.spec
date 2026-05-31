[app]

title = PokemonBAO
package.name = pokemonbao
package.domain = org.pokemonbao

source.dir = .
source.include_exts = py,png,jpg,json

version = 0.1

requirements = python3,pygame==2.5.0

orientation = landscape

fullscreen = 0

android.permissions = INTERNET
android.allow_backup = True

android.ndk_api = 21

android.archs = arm64-v8a, armeabi-v7a

android.icon = %(source.dir)s/assets/icon.png

[buildozer]

log_level = 2

warn_on_root = 1

build_dir = ./.buildozer
bin_dir = ./bin

android.add_assets = assets/
android.accept_sdk_license = True
