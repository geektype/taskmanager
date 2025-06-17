#!/bin/bash

# Start Xvfb
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Start Flask in the background
echo 'Starting Flask'
python app.py > flask.log 2>&1 &
FLASK_PID=$!
sleep 10
cat flask.log

# Wait for Flask to start
echo 'Waiting for flask to start'
for i in {1..30}; do
    if curl -s http://localhost:5000 > /dev/null; then
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "Flask failed to start"
        kill $FLASK_PID
        exit 1
    fi
    sleep 1
done
echo 'Flask Started successfully'

# Run tests
# curl -s -o /dev/null -w "%{http_code}\n" localhost:5000
# echo "Running Tests"
# python -m unittest tests/test_task_manager.py
# TEST_EXIT_CODE=$?
#
# # Kill Flask process
# kill $FLASK_PID
#
# exit $TEST_EXIT_CODE
