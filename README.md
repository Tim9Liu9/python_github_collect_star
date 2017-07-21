# python_github_collect_star
读取data_files文件夹里面的md格式项目[https://github.com/Tim9Liu9/TimLiu-iOS](https://github.com/Tim9Liu9/TimLiu-iOS)，收集里面github上项目的star数、fork数、watch数,并且写回md文件里面去，同时检测github上的项目是否已经不存在，如果项目不存在，项目url写入：logs/stars_url_error.log 文件中。    
技术栈：python3.x、requests的网络请求、BeautifulSoup4的css解析、logging的error保存到日志文件里面、threading多线程执行任务、re有点点复杂的正则表达式
