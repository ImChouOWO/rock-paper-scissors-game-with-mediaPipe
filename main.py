import cv2
import mediapipe as mp 
import random
import time
import threading



currentTurn = 0
nextTurn = 0
gameAction = None
countDown = 5


def computer_gesture():
    return random.choice(['Rock', 'Scissors', 'Papper'])

def change_turn():
    global currentTurn, nextTurn, gameAction, countDown
    if currentTurn != nextTurn:
        currentTurn = nextTurn
        countDown = 5
        gameAction = computer_gesture()
        print(f"now Turn:{currentTurn}")

gameContinue  =False
textChange = False
def countdown_timer():
    global countDown,nextTurn,gameContinue
    while countDown > 0:
        time.sleep(1)
        countDown -= 1
        if not gameContinue and countDown<=0:
            countDown =3
            gameContinue =True
            
    if countDown <=0 and gameContinue == True:
        nextTurn +=1
        gameContinue = False
    

def judge(player, computer):
    global countDown,gameContinue
    if countDown > 0 and not gameContinue :  # 如果倒數計時還沒結束，不做判定

        return "Waiting..."
    else:
        if player == computer:
            
            result = 'Tie'
        elif (player == 'Scissors' and computer == 'Papper') or \
            (player == 'Papper' and computer == 'Rock') or \
            (player == 'Rock' and computer == 'Scissors'):
            
            result = 'Player Win'
        else:

            result = 'Computer Win'
        
        # 如果有結果，開始新回合的倒數計時
        if result != "Waiting..." and not gameContinue:
            change_turn()
            camera.start_new_round()

        return result



def detect_gesture(marks):
        # 判斷指尖是否伸直
        thumb_extended = marks.landmark[4].y > marks.landmark[3].y
        index_extended = marks.landmark[8].y < marks.landmark[6].y
        middle_extended = marks.landmark[12].y < marks.landmark[10].y
        ring_extended = marks.landmark[16].y < marks.landmark[14].y
        pinky_extended = marks.landmark[20].y < marks.landmark[18].y

        extended_fingers = [thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]
        
        # 根據伸直的指尖數量判斷手勢
        if sum(extended_fingers) == 0:
            return "Rock"
        elif sum(extended_fingers) == 2 and index_extended and middle_extended:
            return "Scissors"
        elif sum(extended_fingers) == 4:
            return "Papper"
        else:
            return "Undefind"


class Camera():
    def __init__(self) -> None:
        self.mainCamera = cv2.VideoCapture(0)
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mpDraw = mp.solutions.drawing_utils
        self.handLmsStyle = self.mpDraw.DrawingSpec(color=(0, 0, 255), thickness=3)
        self.handConStyle = self.mpDraw.DrawingSpec(color=(0, 255, 0), thickness=5)
        self.pTime = 0
        self.cTime = 0
    def start_new_round(self):
        global countDown
        
        timer_thread = threading.Thread(target=countdown_timer)
        timer_thread.start()
    

    def recode(self):
        global currentTurn, nextTurn, gameAction, countDown
        gameAction = computer_gesture()
        self.start_new_round()  # 開始第一回合的倒數計時

        while True:
           
            ret, img = self.mainCamera.read()
            if ret:
                imgRgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                res = self.hands.process(imgRgb)
                
                if res.multi_hand_landmarks:
                    marks = res.multi_hand_landmarks[0]
                    self.mpDraw.draw_landmarks(img, marks, self.mpHands.HAND_CONNECTIONS,
                                               self.handLmsStyle, self.handConStyle)

                    gesture = detect_gesture(marks)
                    result = judge(gesture, gameAction)
                    cv2.putText(img, "Player: " + gesture, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    # cv2.putText(img, "Computer: " + gameAction, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    cv2.putText(img, "Result: " + result, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
                    cv2.putText(img, "Time left: " + str(countDown) + "s", (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                cv2.imshow("img", img)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        self.mainCamera.release()
        cv2.destroyAllWindows()

camera = Camera()

if __name__ == "__main__":    
    camera.recode()
