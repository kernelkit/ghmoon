set -e

SHA8=$(echo $SHA | head -c8)
URL=https://github.com/$REPO

cat <<EOF
# Test of \`${REPO}@${SHA8}\` by \`$CONTEXT\`

| | |
|-|-|
| Host     | \`$(hostname)\` |
| User     | \`$(whoami)\` |
| Date     | $(date '+%F %T') |
| Context  | \`$CONTEXT\` |
| Repo     | [\`$REPO\`]($URL) |
| Commit   | [\`$SHA8\`]($URL/commit/$SHA) |
| Deploy   | $([ "$DEPLOY_EXITCODE" = 0 ] && echo :white_check_mark: Pass || echo :x: FAIL) |
| Test     | $([ "$TEST_EXITCODE" = 0 ] && echo :white_check_mark: Pass || echo :x: FAIL) |
EOF
echo

echo
case "$DEPLOY_EXITCODE" in
    "")
        echo "## :exclamation: Deploy (DID NOT RUN)"
        ;;
    0)
        echo "## :white_check_mark: Deploy (Pass)"
        ;;
    *)
        echo "## :x: Deploy (FAIL)"
        ;;
esac
echo

if [ "$DEPLOY_EXITCODE" -a "$REPORT_DEPLOY_SUMMARY" ]; then
    echo "$REPORT_DEPLOY_SUMMARY" | sh
else
        echo "Deploy hook exited with code $DEPLOY_EXITCODE"
fi
echo

if [ -r "$DEPLOY_LOG" ]; then
    cat <<EOF
<details>
<summary><b>Click to show deployment log</b></summary>

\`\`\`
$(cat "$DEPLOY_LOG")
\`\`\`

</details>
EOF
else
    echo _No deployment log captured_
fi
echo

echo
case "$TEST_EXITCODE" in
    "")
        echo "## :exclamation: Test (DID NOT RUN)"
        ;;
    0)
        echo "## :white_check_mark: Test (Pass)"
        ;;
    *)
        echo "## :x: Test (FAIL)"
        ;;
esac
echo

if [ "$TEST_EXITCODE" -a "$REPORT_TEST_SUMMARY" ]; then
    echo "$REPORT_TEST_SUMMARY" | sh
else
    echo "Test hook exited with code $TEST_EXITCODE"
fi
echo

if [ -r "$TEST_LOG" ]; then
    cat <<EOF
<details>
<summary><b>Click to show full test log</b></summary>

\`\`\`
$(cat "$TEST_LOG")
\`\`\`

</details>
EOF
else
    echo _No test log captured_
fi
