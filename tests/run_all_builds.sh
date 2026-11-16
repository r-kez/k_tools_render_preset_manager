#!/bin/bash
# Usage: bash tests/run_all_builds.sh [out_dir]   (BLENDER_BUILDS overrides the builds folder)
# Runs every test in every supported build (Blender >= 4.2) in parallel.
ADDON="$(cd "$(dirname "$0")/.." && pwd)"; OUT="${1:-${TMPDIR:-/tmp}/render_preset_matrix}"; mkdir -p "$OUT/pkg"; rm -f "$OUT"/*.summary "$OUT"/*.log "$OUT"/pkg/*.zip
TESTS="
  blender_native_capture
  blender_octane_preview_paths
  blender_cycles_capture
  blender_output_capture_smoke
  blender_output_experimental
  blender_output_save_load
  blender_blacklist_sync
  blender_output_matrix
"
BUILDS="blender-4.2.15 blender-4.5.4 blender-5.2.0-beta blender-5.3.0-beta blender-5.4.0-alpha OctaneBlender29.19.0 OctaneBlender30.11.0"
ROOT="${BLENDER_BUILDS:-/f/Blender Builds}"
cd "$ADDON"
"$ROOT/blender-4.5.4/blender.exe" --command extension build --source-dir "$ADDON" --output-dir "$OUT/pkg" > "$OUT/build.log" 2>&1
ZIP=$(ls "$OUT/pkg"/*.zip | head -1)

run_build() {
  name="$1"; B="$ROOT/$name/blender.exe"
  for t in $TESTS; do
    timeout 300 "$B" --background --factory-startup --python-exit-code 1 --python "tests/$t.py" > "$OUT/$name.$t.log" 2>&1
    echo "$name $t exit=$?" >> "$OUT/$name.summary"
  done
  P="$OUT/profile/$name"; mkdir -p "$P"
  export BLENDER_USER_RESOURCES="$(cygpath -w "$P")"
  "$B" --command extension install-file -r user_default -e "$ZIP" > "$OUT/$name.install.log" 2>&1
  timeout 300 "$B" --background --python-exit-code 1 --python "tests/blender_extension_profile.py" > "$OUT/$name.blender_extension_profile.log" 2>&1
  echo "$name blender_extension_profile exit=$?" >> "$OUT/$name.summary"
}
for name in $BUILDS; do run_build "$name" & done
wait
cat "$OUT"/*.summary | awk '{split($3,a,"="); s[$1]=s[$1] (a[2]=="0" ? "." : "F:" $2 " ")} END {for (k in s) print k, s[k]}' | sort
echo "--- failures"; grep -h "exit=[^0]" "$OUT"/*.summary
grep -h "CYCLES_CAPTURE_OK\|OUTPUT_CAPTURE_SMOKE_OK\|EXTENSION_PROFILE_RESULT" "$OUT"/*.log | sort
