#!/bin/sh
# Picked at kitty startup via `geninclude` in kitty.conf.
# Prints a random dark theme's config to stdout, which kitty includes inline.
# Swap themes by adding/removing .conf files in ~/.config/kitty/themes/
dir="$HOME/.config/kitty/themes"
theme=$(find "$dir" -maxdepth 1 -name '*.conf' | shuf -n1)
[ -z "$theme" ] && exit 0
echo "# random-theme: $(basename "$theme")"
cat "$theme"
