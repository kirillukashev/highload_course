#!/bin/bash

# здесь все результаты
mkdir -p test_results

# GET
# тест с 3 серверами (через nginx)
ab -n 100000 -c 100 http://localhost:9010/date > test_results/get_3_servers.txt

# Тест с 1 сервером (без nginx)
ab -n 100000 -c 100 http://localhost:9000/date > test_results/get_1_server.txt

# POST
#тест с 3 серверами (через nginx)
ab -n 10000 -c 10 -p post.json -T application/json http://localhost:9010/name > test_results/post_3_servers.txt

# тест с 1 сервером (без nginx)
ab -n 10000 -c 10 -p post.json -T application/json http://localhost:9000/name > test_results/post_1_server.txt
