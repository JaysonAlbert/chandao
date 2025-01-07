#!/bin/bash

# 项目路径列表
directories=(
    "project"
)

author=user

# 默认日期范围
since_date="2024-01-01"
until_date="2024-12-31"
# 默认阈值
threshold=5000

# 如果传入了日期范围参数，则使用传入的日期
if [ -n "$2" ] && [ -n "$3" ]; then
    since_date=$2
    until_date=$3
fi

if [ -n "$4" ]; then
    threshold=$4
fi

echo "Using date range: $since_date to $until_date"
echo "Using threshold: $threshold"

# 统计新增行数的函数
function count_lines_added() {

    # 循环遍历目录并执行 git log
    for dir in "${directories[@]}"
    do
        echo "Processing directory: $dir"
        
        # 进入目录
        cd "$dir" || continue
        
        # 执行 git log 命令并统计
        git log --all --author="$author" --pretty=tformat: --since="$since_date" --until="$until_date" --numstat --no-merges | \
        awk '{ add += $1 ; subs += $2 ; loc += $1 + $2 } END { printf "added lines: %s removed lines : %s total lines: %s\n",add,subs,loc }'
        
        echo "------------------------"
    done
}

# 查找新增行数超过5000行的提交的函数
function find_large_commits() {

    # 循环处理每个项目目录
    for project_dir in "${directories[@]}"
    do
        echo "Processing project: $project_dir"
        
        # 进入项目目录
        cd "$project_dir" || continue
        
        # 遍历某时间段内的每次提交
        git log --all --author="$author" --since="$since_date" --until="$until_date" --pretty=format:"%H" --no-merges | while read commit_hash
        do
            # 获取当前提交的 diff 统计信息
            diff_stat=$(git show --stat --oneline "$commit_hash" | tail -n 1)
            
            # 提取新增行数
            added_lines=$(echo "$diff_stat" | awk '{print $4}')
            

            if [[ "$added_lines" =~ ^[0-9]+$ ]]; then
                # 检查新增行数是否超过阈值
                if [[ "$added_lines" -gt "$threshold" ]]
                then
                    # 输出符合条件的提交
                    echo "In project $project_dir: Commit $commit_hash added $added_lines lines"
                fi
            fi
        done
        
        echo "------------------------"
    done
}

# 主逻辑
if [ "$1" == "count" ]; then
    # 调用 count_lines_added 函数并传入阈值（如果有）
    count_lines_added "$@"
elif [ "$1" == "find" ]; then
    # 调用 find_large_commits 函数并传入日期范围（如果有）
    find_large_commits "$@"
else
    echo "Usage: $0 {count|find} [start_date] [end_date] [threshold]"
    echo "  count  : Count the added lines in commits"
    echo "           Optionally, specify a threshold for added lines"
    echo "  find   : Find commits with added lines greater than 5000"
    echo "           Optionally, specify a start date and end date (format: YYYY-MM-DD)"
fi
