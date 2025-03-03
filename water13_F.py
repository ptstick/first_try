import RPi.GPIO as GPIO
import time
import threading
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# GPIO 핀 설정
GPIO_PINS = {
    "sol_valve_00": 19,
    "sol_valve_01": 13,
    "sol_valve_02": 6,
    "sol_valve_03": 5
}

GPIO.setmode(GPIO.BCM)
for pin in GPIO_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

# 상태 변수
outputStates = {pin: "off" for pin in GPIO_PINS}

# 최소 및 최대 시간 설정 (분 단위)
MIN_TIME = 1  # 최소 1분
MAX_TIME = 120  # 최대 120분

def timer_off(pin, time_in_minutes):
    """ 타이머가 종료되면 자동으로 해당 장치를 off """
    time.sleep(time_in_minutes * 60)  # 시간 (분) 단위로 대기
    GPIO.output(GPIO_PINS[pin], GPIO.LOW)
    outputStates[pin] = "off"
    print(f"{pin} OFF - 타이머 종료")

    # 타이머 종료 후 상태를 갱신할 수 있도록 클라이언트에 알리기
    with app.test_request_context():
        app.jinja_env.globals['outputStates'] = outputStates

@app.route('/status')
def get_status():
    # 클라이언트에게 현재 장치들의 상태를 반환
    return outputStates

@app.route('/')
def index():
    global outputStates
    html = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>자동화 관수 시스템</title>
        <script src="{{ url_for('static', filename='js/jquery-3.6.0.min.js') }}"></script>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
            }
            h1 {
                font-size: 36px;
                margin-top: 30px;
                margin-bottom: 10px;
                color: #000000;
                text-align: center;
            }
            .container {
                max-width: 800px;
                margin: auto;
            }
            .button-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;  /* 버튼들을 중앙에 배치 */
                margin-top: 20px;
            }
            .button-container .row {
                display: flex;
                justify-content: center;  /* 버튼들을 가로로 중앙 정렬 */
                align-items: center;  /* 세로로 중앙 정렬 */
                width: 100%;
                margin-bottom: 10px;
            }
            .button-container .row .btn {
                width: 200px;
                height: 80px;
                font-size: 20px;
                margin: 10px;
                border-radius: 50px;
                text-align: center;
            }
            .btn-on {
                background-color: #f44336;
                border: none;
                color: white;
            }
            .btn-off {
                background-color: #4CAF50;
                border: none;
                color: white;
            }
            .btn-on:hover, .btn-off:hover {
                opacity: 0.8;
            }

            .logo {
                width: 80px;  /* 로고 크기 */
                height: auto;
                position: absolute;
                top: 20px;
                left: 20px;
            }

            /* 반응형 디자인: 모바일 화면에서 버튼 크기 조정 */
            @media (max-width: 600px) {
                .button-container .btn {
                    width: 100%;  /* 버튼의 너비를 100%로 설정 */
                    height: 60px;  /* 버튼 높이 줄이기 */
                    font-size: 16px;  /* 글씨 크기 줄이기 */
                    margin: 5px 0;  /* 버튼 간 여백 조정 */
                }
                .button-container .row {
                    flex-direction: column;  /* 버튼들을 세로로 배치 */
                    align-items: center;  /* 세로 중앙 정렬 */
                }
            }

        </style>
        <script>
            // 상태 갱신을 위한 AJAX 요청
            function refreshStatus() {
                $.get("/status", function(data) {
                    for (let pin in data) {
                        // 상태가 변경되더라도 버튼의 스타일은 그대로 유지하고 상태만 변경
                        if (data[pin] === 'off') {
                            $('#' + pin).removeClass("btn-on").addClass("btn-off");
                            // OFF 상태일 때 텍스트 변경
                            let label = pin.replace("_", " ");
                            if (pin === 'sol_valve_00') {
                                $('#' + pin).text("1구역 솔밸브 설정");
                            } else if (pin === 'sol_valve_01') {
                                $('#' + pin).text("2구역 솔밸브 설정");
                            } else if (pin === 'sol_valve_02') {
                                $('#' + pin).text("3구역 솔밸브 설정");
                            } else if (pin === 'sol_valve_03') {
                                $('#' + pin).text("4구역 솔밸브 설정");
                            } else {
                                $('#' + pin).text(label + " 설정");
                            }
                        } else {
                            $('#' + pin).removeClass("btn-off").addClass("btn-on");
                            // ON 상태일 때 텍스트 변경
                            let label = pin.replace("_", " ");
                            if (pin === 'sol_valve_00') {
                                $('#' + pin).text("1구역 솔밸브 OFF");
                            } else if (pin === 'sol_valve_01') {
                                $('#' + pin).text("2구역 솔밸브 OFF");
                            } else if (pin === 'sol_valve_02') {
                                $('#' + pin).text("3구역 솔밸브 OFF");
                            } else if (pin === 'sol_valve_03') {
                                $('#' + pin).text("4구역 솔밸브 OFF");
                            } else {
                                $('#' + pin).text(label + " OFF");
                            }
                        }
                    }
                });
            }
            // 일정 시간 간격으로 상태 업데이트_(3초마다)_5초는 반응이 늦어보임..250205
            setInterval(refreshStatus, 3000);
        </script>
    </head>
    <body>
        <img src="{{ url_for('static', filename='logo.png') }}" class="logo" alt="Logo">
        <div class="container">
            <h1>자동화 관수 시스템</h1>
            <div class="button-container">
                <div class="row">
                    <p>
                        {% if outputStates["sol_valve_00"] == 'off' %}
                            <a href="/sol_valve_00/settings"><button id="sol_valve_00" class="btn btn-off">1구역 솔밸브 설정</button></a>
                        {% else %}
                            <a href="/sol_valve_00/off"><button id="sol_valve_00" class="btn btn-on">1구역 솔밸브 OFF</button></a>
                        {% endif %}
                    </p>
                    <p>
                        {% if outputStates["sol_valve_01"] == 'off' %}
                            <a href="/sol_valve_01/settings"><button id="sol_valve_01" class="btn btn-off">2구역 솔밸브 설정</button></a>
                        {% else %}
                            <a href="/sol_valve_01/off"><button id="sol_valve_01" class="btn btn-on">2구역 솔밸브 OFF</button></a>
                        {% endif %}
                    </p> 
                </div>
                <div class="row">
                    <p>
                        {% if outputStates["sol_valve_02"] == 'off' %}
                            <a href="/sol_valve_02/settings"><button id="sol_valve_02" class="btn btn-off">3구역 솔밸브 설정</button></a>
                        {% else %}
                            <a href="/sol_valve_02/off"><button id="sol_valve_02" class="btn btn-on">3구역 솔밸브 OFF</button></a>
                        {% endif %}
                    </p>
                    <p>
                        {% if outputStates["sol_valve_03"] == 'off' %}
                            <a href="/sol_valve_03/settings"><button id="sol_valve_03" class="btn btn-off">4구역 솔밸브 설정</button></a>
                        {% else %}
                            <a href="/sol_valve_03/off"><button id="sol_valve_03" class="btn btn-on">4구역 솔밸브 OFF</button></a>
                        {% endif %}
                    </p> 
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, outputStates=outputStates)

@app.route('/<pin>/settings')
def settings(pin):
    return render_template_string(""" 
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>솔밸브 타이머 설정</title>
        <script src="{{ url_for('static', filename='js/jquery-3.6.0.min.js') }}"></script>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
            }
            h1 {
                font-size: 36px;
                margin-top: 30px;
                margin-bottom: 20px;
                text-align: center;
            }
            .logo {
                width: 80px;  /* 로고 크기 */
                height: auto;
                position: absolute;
                top: 20px;
                left: 20px;
            }
            .container {
                max-width: 800px;
                margin: auto;
            }
            .button-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;  /* 버튼들을 중앙에 배치 */
                margin-top: 20px;
            }
            .button-container .row {
                display: flex;
                justify-content: center;  /* 버튼들을 가로로 중앙 정렬 */
                align-items: center;  /* 세로로 중앙 정렬 */
                width: 100%;
                margin-bottom: 10px;
            }
            .button-container .row .btn-custom {
                width: 200px;  /* 버튼의 너비 */
                height: 80px;  /* 버튼의 높이 */
                font-size: 20px;  /* 버튼 글씨 크기 */
                margin: 10px;
                border-radius: 50px;
                text-align: center;
            }
            .btn-success {
                background-color: #4CAF50;
                border: none;
                color: white;
            }
            .btn-primary {
                background-color: #2196F3;
                border: none;
                color: white;
            }
            .btn-danger {
                background-color: #f44336;
                border: none;
                color: white;
            }
            .btn-custom:hover {
                opacity: 0.8;
            }
            
            /* '이전' 버튼을 각진 네모로 만들기 */
            .btn-back {
                background-color: #ccc;
                color: black;
                width: 100px;  /* 이전 버튼도 동일한 너비 설정 */
                height: 50px;  /* 동일한 높이 설정 */
                font-size: 20px;  /* 동일한 글씨 크기 */
                margin: 10px;
                text-align: center;
                border-radius: 0;  /* 각진 네모로 변경 */
            }

            /* 반응형 디자인: 모바일 화면에서 버튼 크기 조정 */
            @media (max-width: 600px) {
                .button-container .btn-custom {
                    width: 100%;  /* 버튼의 너비를 100%로 설정 */
                    height: 60px;  /* 버튼 높이 줄이기 */
                    font-size: 16px;  /* 글씨 크기 줄이기 */
                    margin: 5px 0;  /* 버튼 간 여백 조정 */
                }
                .button-container .btn-back {
                    width: 100%;  /* 이전 버튼 너비 100%로 설정 */
                    height: 40px;  /* 이전 버튼 높이 40px로 설정 */
                    font-size: 16px;  /* 이전 버튼 글씨 크기 */
                    margin: 5px 0;  /* 버튼 간 여백 조정 */
                    border-radius: 0;  /* 각진 네모로 설정 */
                }
                .button-container {
                    justify-content: center;  /* 모바일에서 버튼을 중앙에 위치시키기 위해 추가 */
                }
                .button-container .row {
                    flex-direction: column;  /* 버튼들을 세로로 배치 */
                    align-items: center;  /* 세로 중앙 정렬 */
                }
            }

        </style>
    </head>
    <body>
        <img src="{{ url_for('static', filename='logo.png') }}" class="logo" alt="Logo">
        <div class="container">
            <h1>솔밸브 타이머 설정</h1>
            <div class="button-container">
                <div class="row">
                    <a href="/{{ pin }}/on/60"><button class="btn btn-success btn-custom">1시간</button></a>
                    <a href="/{{ pin }}/on/120"><button class="btn btn-success btn-custom">2시간</button></a>
                </div>
                <div class="row">
                    <a href="/{{ pin }}/on/180"><button class="btn btn-success btn-custom">3시간</button></a>
                    <a href="/{{ pin }}/user_settings"><button class="btn btn-primary btn-custom">사용자 설정</button></a>
                </div>
            </div>
            <div class="button-container">
                <a href="/"><button class="btn btn-danger btn-back">이전</button></a>
            </div>
        </div>
    </body>
    </html>
    """, pin=pin)


@app.route('/<pin>/user_settings')
def user_settings(pin):
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>사용자 시간 설정</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f9;
                padding: 20px;
            }
            h1 {
                font-size: 36px;
                margin-top: 30px;
                margin-bottom: 20px;
                text-align: center;
            }
            .logo {
                width: 80px;
                height: auto;
                position: absolute;
                top: 20px;
                left: 20px;
            }
            .input-time {
                margin-top: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 10px;
            }
            .input-time input {
                width: 70%;
                max-width: 400px;
                height: 50px;
                font-size: 16px;
                min-width: 220px;
                padding: 0 12px;
                border-radius: 10px;
                border: 1px solid #ccc;
                text-align: center; /* 중앙 정렬 */
                box-sizing: border-box;
            }
            .btn-primary {
                background-color: #2196F3;
                color: white;
                height: 50px;
                font-size: 16px;
                border-radius: 10px;
                padding: 0 15px;
                cursor: pointer;
                display: flex;
                justify-content: center;
                align-items: center;
                box-sizing: border-box;
                white-space: nowrap; /* 버튼 텍스트 줄바꿈 방지 */
            }
            .btn-back-container {
                display: flex;
                justify-content: center;
                margin-top: 30px;
            }
            .btn-back {
                background-color: #ccc;
                color: black;
                width: 100px;
                height: 50px;
                font-size: 20px;
                margin: 10px;
                text-align: center;
                border-radius: 0;
                outline: none;
            }
            @media (max-width: 600px) {
                .input-time input {
                    width: 90%;
                    font-size: 14px;
                    height: 50px;
                }
                .btn-back {
                    width: 100%;
                    height: 40px;
                    font-size: 16px;
                    margin: 5px 0;
                }
            }
            h3 {
                text-align: center;
            }
        </style>
    </head>
    <body>
        <img src="{{ url_for('static', filename='logo.png') }}" class="logo" alt="Logo">
        <h1>사용자 시간 설정</h1>
        <h3>사용자 시간을 입력하세요 (최소 {{ MIN_TIME }}분, 최대 {{ MAX_TIME }}분):</h3>
        <div class="input-time">
            <form action="/{{ pin }}/on/custom" method="POST" style="display: flex; gap: 10px;">
                <input type="number" name="custom_time" min="{{ MIN_TIME }}" max="{{ MAX_TIME }}" placeholder="분 단위로 입력" required>
                <button type="submit" class="btn btn-primary">설정</button>
            </form>
        </div>
        <div class="btn-back-container">
            <a href="/{{ pin }}/settings"><button class="btn btn-danger btn-back">이전</button></a>
        </div>
    </body>
    </html>
    """, pin=pin, MIN_TIME=MIN_TIME, MAX_TIME=MAX_TIME)



@app.route('/<pin>/on/custom', methods=["POST"])
def control_pin_custom(pin):
    global outputStates
    try:
        custom_time = int(request.form["custom_time"])
        if custom_time < MIN_TIME or custom_time > MAX_TIME:
            return redirect(url_for('settings', pin=pin))  # 범위 벗어나면 이전 페이지로 돌아감
    except ValueError:
        return redirect(url_for('settings', pin=pin))  # 잘못된 입력 처리
    GPIO.output(GPIO_PINS[pin], GPIO.HIGH)
    outputStates[pin] = "on"
    threading.Thread(target=timer_off, args=(pin, custom_time)).start()
    return redirect(url_for('index'))

@app.route('/<pin>/on/<time_in_minutes>')
def control_pin(pin, time_in_minutes):
    time_in_minutes = int(time_in_minutes)
    GPIO.output(GPIO_PINS[pin], GPIO.HIGH)
    outputStates[pin] = "on"
    threading.Thread(target=timer_off, args=(pin, time_in_minutes)).start()
    return redirect(url_for('index'))

@app.route('/<pin>/off')
def turn_off(pin):
    GPIO.output(GPIO_PINS[pin], GPIO.LOW)
    outputStates[pin] = "off"
    return redirect(url_for('index'))

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=80)
    finally:
        GPIO.cleanup()
