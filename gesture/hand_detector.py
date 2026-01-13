"""
Modulo di riconoscimento gesti della mano usando MediaPipe
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Optional, Tuple, List
import time

class HandDetector:
    """
    Classe per il rilevamento e riconoscimento dei gesti della mano.
    Utilizza MediaPipe per il tracking dei landmark della mano.
    """
    
    def __init__(self, 
                 max_hands: int = 1,
                 detection_confidence: float = 0.7,
                 tracking_confidence: float = 0.7):
        """
        Inizializza il rilevatore di mani.
        
        Args:
            max_hands: Numero massimo di mani da rilevare
            detection_confidence: Soglia di confidenza per il rilevamento
            tracking_confidence: Soglia di confidenza per il tracking
        """
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        
        # Indici dei landmark per ogni dito
        self.finger_tips = [4, 8, 12, 16, 20]  # Pollice, Indice, Medio, Anulare, Mignolo
        self.finger_pips = [3, 6, 10, 14, 18]  # Articolazioni intermedie
        
        # Per il tracking del gesto nel tempo
        self.last_gesture = None
        self.gesture_start_time = 0
        self.gesture_confirmed = False
        
    def find_hands(self, frame: np.ndarray, draw: bool = True) -> Tuple[np.ndarray, List]:
        """
        Trova le mani nel frame e opzionalmente disegna i landmark.
        
        Args:
            frame: Frame BGR da OpenCV
            draw: Se True, disegna i landmark sul frame
            
        Returns:
            Tuple con il frame processato e la lista dei risultati
        """
        # Converti in RGB per MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        all_hands = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                   results.multi_handedness):
                # Estrai informazioni sulla mano
                hand_info = {
                    'landmarks': hand_landmarks,
                    'handedness': handedness.classification[0].label,
                    'confidence': handedness.classification[0].score
                }
                all_hands.append(hand_info)
                
                # Disegna i landmark
                if draw:
                    self.mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_styles.get_default_hand_landmarks_style(),
                        self.mp_styles.get_default_hand_connections_style()
                    )
        
        return frame, all_hands
    
    def get_finger_states(self, hand_landmarks, frame_shape: Tuple[int, int]) -> List[bool]:
        """
        Determina quali dita sono estese.
        
        Args:
            hand_landmarks: Landmark della mano da MediaPipe
            frame_shape: (height, width) del frame
            
        Returns:
            Lista di 5 booleani [pollice, indice, medio, anulare, mignolo]
        """
        h, w = frame_shape[:2]
        landmarks = hand_landmarks.landmark
        
        fingers = []
        
        # Pollice - confronta x invece di y (movimento laterale)
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        thumb_mcp = landmarks[2]
        
        # Il pollice è esteso se la punta è più lontana dal palmo
        thumb_extended = abs(thumb_tip.x - thumb_mcp.x) > abs(thumb_ip.x - thumb_mcp.x)
        fingers.append(thumb_extended)
        
        # Altri 4 dita - confronta y (punta sopra l'articolazione = esteso)
        for tip_idx, pip_idx in zip(self.finger_tips[1:], self.finger_pips[1:]):
            tip = landmarks[tip_idx]
            pip = landmarks[pip_idx]
            # Y più basso = più in alto nel frame
            fingers.append(tip.y < pip.y)
        
        return fingers
    
    def recognize_gesture(self, hand_landmarks, frame_shape: Tuple[int, int]) -> str:
        """
        Riconosce il gesto della mano basandosi sui landmark.
        
        Args:
            hand_landmarks: Landmark della mano da MediaPipe
            frame_shape: (height, width) del frame
            
        Returns:
            Stringa identificativa del gesto riconosciuto
        """
        fingers = self.get_finger_states(hand_landmarks, frame_shape)
        landmarks = hand_landmarks.landmark
        
        # Conta le dita estese
        extended_count = sum(fingers)
        
        # === GESTI DI GIOCO ===
        
        # SASSO: Tutte le dita chiuse (pugno)
        # Now require zero extended fingers so that a single index finger
        # can be recognized as point_up/point_down instead of being
        # misclassified as 'rock'.
        if extended_count == 0:
            return 'rock'
        
        # CARTA: Tutte le dita estese (mano aperta)
        if extended_count >= 4:
            return 'paper'
        
        # FORBICE: Solo indice e medio estesi
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            return 'scissors'
        
        # === GESTI DI NAVIGAZIONE ===
        
        # PUNTA GIU: Solo indice esteso verso il basso (usato per navigazione down)
        if fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
            index_tip = landmarks[8]
            index_mcp = landmarks[5]
            if index_tip.y > index_mcp.y:
                return 'point_down'
        
        return 'none'
    
    def get_confirmed_gesture(self, gesture: str, hold_time: float = 0.5) -> Optional[str]:
        """
        Conferma un gesto solo se mantenuto per un certo tempo.
        
        Args:
            gesture: Il gesto attualmente rilevato
            hold_time: Tempo in secondi per confermare il gesto
            
        Returns:
            Il gesto confermato o None
        """
        current_time = time.time()
        
        if gesture != self.last_gesture:
            # Nuovo gesto, resetta il timer
            self.last_gesture = gesture
            self.gesture_start_time = current_time
            self.gesture_confirmed = False
            return None
        
        # Stesso gesto, controlla il tempo
        if current_time - self.gesture_start_time >= hold_time:
            if not self.gesture_confirmed:
                self.gesture_confirmed = True
                return gesture
        
        return None
    
    def get_gesture_progress(self, hold_time: float = 0.5) -> float:
        """
        Restituisce il progresso della conferma del gesto (0-1).
        
        Args:
            hold_time: Tempo totale richiesto per confermare
            
        Returns:
            Progresso da 0.0 a 1.0
        """
        if self.last_gesture is None or self.last_gesture == 'none':
            return 0.0
        
        elapsed = time.time() - self.gesture_start_time
        return min(1.0, elapsed / hold_time)
    
    def reset_gesture_tracking(self):
        """Resetta il tracking del gesto."""
        self.last_gesture = None
        self.gesture_start_time = 0
        self.gesture_confirmed = False
    
    def get_hand_center(self, hand_landmarks, frame_shape: Tuple[int, int]) -> Tuple[int, int]:
        """
        Calcola il centro della mano.
        
        Args:
            hand_landmarks: Landmark della mano
            frame_shape: (height, width) del frame
            
        Returns:
            Tuple (x, y) del centro della mano in pixel
        """
        h, w = frame_shape[:2]
        landmarks = hand_landmarks.landmark
        
        # Usa il palmo (landmark 0) come centro
        palm = landmarks[0]
        return int(palm.x * w), int(palm.y * h)
    
    def release(self):
        """Rilascia le risorse."""
        self.hands.close()


class CameraManager:
    """
    Gestisce l'accesso alla webcam.
    """
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Inizializza la camera.
        
        Args:
            camera_index: Indice della webcam
            width: Larghezza del frame
            height: Altezza del frame
        """
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Impossibile aprire la camera {camera_index}")
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    def read(self, flip: bool = True) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Legge un frame dalla camera.
        
        Args:
            flip: Se True, specchia il frame orizzontalmente
            
        Returns:
            Tuple (success, frame)
        """
        ret, frame = self.cap.read()
        
        if ret and flip:
            frame = cv2.flip(frame, 1)
        
        return ret, frame
    
    def release(self):
        """Rilascia la camera."""
        self.cap.release()
    
    def is_opened(self) -> bool:
        """Verifica se la camera è aperta."""
        return self.cap.isOpened()
