"""
Modulo di riconoscimento gesti della mano usando MediaPipe
"""

import cv2
import importlib
try:
    import mediapipe as mp
except Exception:
    mp = None
import numpy as np
from typing import Optional, Tuple, List, Dict
import os
import importlib
import time
from collections import deque
import math

# Importa configurazioni
try:
    from config import GESTURE_DETECTION
except ImportError:
    # Valori di default se config non è disponibile
    GESTURE_DETECTION = {
        'min_detection_confidence': 0.7,
        'min_tracking_confidence': 0.7,
        'temporal_smoothing_frames': 5,
        'fist_closure_threshold': 1.8,
        'scissors_v_ratio_excellent': 1.3,
        'scissors_v_ratio_good': 1.1,
        'finger_extension_margin': 0.02,
        'finger_extension_distance_ratio': 1.15,
    }

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
        # Compatibilità con diverse release di MediaPipe:
        # - Se è presente l'API legacy `mp.solutions`, la useremo (mp<=0.8.x).
        # - Altrimenti proviamo la Task API (mp>=0.10) tramite
        #   mediapipe.tasks.python.vision.HandLandmarker.
        self.use_solutions = False
        self.use_tasks = False

        # Primo tentativo: api legacy `mp.solutions`
        if hasattr(mp, 'solutions'):
            try:
                self.mp_hands = mp.solutions.hands
                self.mp_draw = mp.solutions.drawing_utils
                self.mp_styles = mp.solutions.drawing_styles
                self.hands = self.mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=max_hands,
                    min_detection_confidence=detection_confidence,
                    min_tracking_confidence=tracking_confidence
                )
                self.use_solutions = True
            except Exception:
                self.use_solutions = False

        # Se legacy non disponibile, proviamo la Task API (v0.10+)
        if not self.use_solutions:
            try:
                from mediapipe.tasks.python import vision as mp_vision
                from mediapipe.tasks.python import BaseOptions

                # Cerca il modello in percorsi comuni o in config
                try:
                    from config import HAND_LANDMARKER_MODEL
                except Exception:
                    HAND_LANDMARKER_MODEL = 'models/hand_landmarker.task'

                candidate_paths = [
                    HAND_LANDMARKER_MODEL,
                    os.path.join('models', 'hand_landmarker.task'),
                    'hand_landmarker.task',
                    'hand_landmarker.tflite',
                    os.path.join('models', 'hand_landmarker.tflite'),
                ]

                model_path = None
                for p in candidate_paths:
                    if p and os.path.exists(p):
                        model_path = p
                        break

                if model_path is None:
                    # Non blocchiamo l'inizializzazione: abilita fallback (nessun riconoscimento)
                    self.use_tasks = False
                    self.disabled_reason = (
                        "Modello MediaPipe HandLandmarker non trovato. "
                        "Scarica il file modello (es. hand_landmarker.task) e mettilo in 'models/'. "
                        "Vedi la documentazione MediaPipe per il modello da usare."
                    )
                else:
                    # Costruisci le opzioni per la modalità video
                    options = mp_vision.HandLandmarkerOptions(
                        base_options=BaseOptions(model_asset_path=model_path),
                        running_mode=mp_vision.RunningMode.VIDEO,
                        num_hands=max_hands,
                        min_hand_detection_confidence=detection_confidence,
                        min_tracking_confidence=tracking_confidence,
                    )

                    self.hand_landmarker = mp_vision.HandLandmarker.create_from_options(options)
                    self.mp_draw = mp_vision.drawing_utils
                    self.mp_styles = mp_vision.drawing_styles if hasattr(mp_vision, 'drawing_styles') else None
                    self.use_tasks = True
            except Exception as e:
                # Non blocchiamo l'inizializzazione: mettiamo un flag di disabilitazione
                self.use_tasks = False
                self.disabled_reason = (
                    "Impossibile inizializzare MediaPipe via Task API. "
                    f"Dettaglio: {e}"
                )
        
        # `self.hands` è già creato per mp.solutions; per tasks abbiamo `self.hand_landmarker`.
        
        # Indici dei landmark per ogni dito
        self.finger_tips = [4, 8, 12, 16, 20]  # Pollice, Indice, Medio, Anulare, Mignolo
        self.finger_pips = [3, 6, 10, 14, 18]  # Articolazioni intermedie
        self.finger_mcps = [2, 5, 9, 13, 17]   # Articolazioni base
        
        # Per il tracking del gesto nel tempo
        self.last_gesture = None
        self.gesture_start_time = 0
        self.gesture_confirmed = False
        
        # Smoothing temporale per ridurre jitter
        smoothing_frames = GESTURE_DETECTION.get('temporal_smoothing_frames', 5)
        self.gesture_history = deque(maxlen=smoothing_frames)
        self.confidence_history = deque(maxlen=smoothing_frames)
        
    def find_hands(self, frame: np.ndarray, draw: bool = True) -> Tuple[np.ndarray, List]:
        """
        Trova le mani nel frame e opzionalmente disegna i landmark.
        
        Args:
            frame: Frame BGR da OpenCV
            draw: Se True, disegna i landmark sul frame
            
        Returns:
            Tuple con il frame processato e la lista dei risultati
        """
        all_hands = []

        if self.use_solutions:
            # Converti in RGB per MediaPipe solutions
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            if results.multi_hand_landmarks:
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                       results.multi_handedness):
                    hand_info = {
                        'landmarks': hand_landmarks,
                        'handedness': handedness.classification[0].label,
                        'confidence': handedness.classification[0].score
                    }
                    all_hands.append(hand_info)

                    if draw:
                        # drawing_styles may not exist in very old versions; guard
                        try:
                            landmark_style = self.mp_styles.get_default_hand_landmarks_style()
                            conn_style = self.mp_styles.get_default_hand_connections_style()
                        except Exception:
                            landmark_style = None
                            conn_style = None
                        self.mp_draw.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            landmark_style,
                            conn_style
                        )

        elif self.use_tasks:
            # Converti BGR->RGB e crea Image per la task API
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Image expects numpy array in HxWxC uint8
            from mediapipe.tasks.python.vision.core.image import Image, ImageFormat
            mp_image = Image(ImageFormat.SRGB, rgb)

            # timestamp in ms
            timestamp_ms = int(time.time() * 1000)
            try:
                result = self.hand_landmarker.detect_for_video(mp_image, timestamp_ms)
            except Exception:
                # Try image detect for compatibility if video mode isn't active
                try:
                    result = self.hand_landmarker.detect(mp_image)
                except Exception:
                    return frame, []

            # result.hand_landmarks is List[List[NormalizedLandmark]]
            if getattr(result, 'hand_landmarks', None):
                for i, landmarks_list in enumerate(result.hand_landmarks):
                    # handedness and confidence may be in result.handedness
                    hand_info = {
                        'landmarks': landmarks_list,
                        'handedness': None,
                        'confidence': 1.0,
                    }
                    # Try to extract handedness
                    try:
                        if hasattr(result, 'handedness') and len(result.handedness) > i:
                            # result.handedness[i] is a list of category lists
                            hand_info['handedness'] = getattr(result.handedness[i][0].categories[0], 'category_name', None)
                            hand_info['confidence'] = getattr(result.handedness[i][0].categories[0], 'score', 1.0)
                    except Exception:
                        pass
                    all_hands.append(hand_info)

                    if draw:
                        try:
                            # draw_landmarks expects list of NormalizedLandmark and connections
                            from mediapipe.tasks.python.vision import HandLandmarksConnections
                            connections = HandLandmarksConnections.HAND_CONNECTIONS
                            # Use drawing_utils from tasks
                            self.mp_draw.draw_landmarks(frame, landmarks_list, connections)
                        except Exception:
                            pass

        return frame, all_hands

    def get_finger_states(self, hand_landmarks, frame_shape: Tuple[int, int]) -> List[bool]:
        """
        Determina lo stato (esteso/chiuso) di ciascun dito.

        Restituisce una lista di 5 booleani corrispondenti a
        [thumb, index, middle, ring, pinky]. Funziona con oggetti
        `hand_landmarks` di MediaPipe solutions (ha `.landmark`) o
        con la lista di NormalizedLandmark usata dalla Task API.
        """
        # Normalizza la rappresentazione dei landmark
        if hasattr(hand_landmarks, 'landmark'):
            landmarks = hand_landmarks.landmark
        else:
            landmarks = hand_landmarks

        h, w = frame_shape[:2]

        margin = GESTURE_DETECTION.get('finger_extension_margin', 0.02)
        distance_ratio = GESTURE_DETECTION.get('finger_extension_distance_ratio', 1.15)

        fingers: List[bool] = []

        # Wrist per riferimento
        wrist = landmarks[0]
        # Calcola una scala di riferimento: distanza tra polso e middle_mcp
        try:
            middle_mcp = landmarks[self.finger_mcps[2]]
            ref_size = self._calculate_distance(wrist, middle_mcp) + 1e-6
        except Exception:
            ref_size = 0.1

        # Thumb: approccio semplice basato su distanza relativa lungo X rispetto al pip
        try:
            thumb_tip = landmarks[self.finger_tips[0]]
            thumb_ip = landmarks[self.finger_pips[0]]
            # Se la distanza del pollice dalla base lungo X è abbastanza grande lo consideriamo esteso
            thumb_ext = abs(thumb_tip.x - thumb_ip.x) > margin * distance_ratio
        except Exception:
            thumb_ext = False

        fingers.append(bool(thumb_ext))

        # Altri 4 dita: controlla se il tip è più alto (y minore) del pip (segno di estensione)
        for tip_idx, pip_idx in zip(self.finger_tips[1:], self.finger_pips[1:]):
            try:
                tip = landmarks[tip_idx]
                pip = landmarks[pip_idx]
                # Normalized coords: y minore => dito verso l'alto (esteso)
                extended = (tip.y < pip.y - margin)

                # Ulteriore controllo: la distanza tip-polso deve essere >= ratio * ref_size
                tip_wrist_dist = self._calculate_distance(tip, wrist)
                if ref_size > 0 and tip_wrist_dist < ref_size * distance_ratio:
                    extended = False

                fingers.append(bool(extended))
            except Exception:
                fingers.append(False)

        return fingers
    
    def _calculate_distance(self, point1, point2) -> float:
        """Calcola la distanza euclidea tra due landmark."""
        return math.sqrt(
            (point1.x - point2.x) ** 2 + 
            (point1.y - point2.y) ** 2 + 
            (point1.z - point2.z) ** 2
        )
    
    def _calculate_angle(self, point1, point2, point3) -> float:
        """
        Calcola l'angolo formato da tre punti (point2 è il vertice).
        Restituisce l'angolo in gradi.
        """
        # Vettori
        v1 = np.array([point1.x - point2.x, point1.y - point2.y, point1.z - point2.z])
        v2 = np.array([point3.x - point2.x, point3.y - point2.y, point3.z - point2.z])
        
        # Calcola l'angolo
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        angle = np.arccos(cos_angle)
        
        return np.degrees(angle)
    
    def _is_fist_closed(self, hand_landmarks, fingers: List[bool]) -> Tuple[bool, float]:
        """
        Verifica se la mano è chiusa a pugno - algoritmo semplificato e permissivo.
        
        Args:
            hand_landmarks: Landmark della mano
            fingers: Stato delle dita
            
        Returns:
            Tupla (is_fist, confidence)
        """
        # Support both MediaPipe solutions (.landmark) and Task API (list)
        if hasattr(hand_landmarks, 'landmark'):
            landmarks = hand_landmarks.landmark
        else:
            landmarks = hand_landmarks
        
        # Se troppe dita estese, non è un pugno
        num_extended = sum(fingers)
        if num_extended >= 3:  # Massimo 2 dita "semi-estese" tollerate
            return False, 0.0
        
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        hand_size = self._calculate_distance(wrist, middle_mcp)
        
        scores = []
        
        # === CRITERIO 1: Compattezza (più permissivo) ===
        all_x = [lm.x for lm in landmarks]
        all_y = [lm.y for lm in landmarks]
        all_z = [lm.z for lm in landmarks]
        
        bbox_width = max(all_x) - min(all_x)
        bbox_height = max(all_y) - min(all_y)
        bbox_depth = max(all_z) - min(all_z)
        bbox_volume = bbox_width * bbox_height * bbox_depth
        
        natural_volume = hand_size ** 3
        compactness_ratio = bbox_volume / (natural_volume + 1e-6)
        
        # Più permissivo: < 35% invece di 20%
        if compactness_ratio < 0.35:
            compactness_score = min(1.0, (0.35 - compactness_ratio) / 0.35 * 1.5)
            scores.append(compactness_score)
        
        # === CRITERIO 2: Distanza Punte dal Polso (semplificato) ===
        tip_distances = []
        for tip_idx in self.finger_tips[1:]:  # Escludi pollice
            dist = self._calculate_distance(landmarks[tip_idx], wrist)
            tip_distances.append(dist)
        
        avg_tip_distance = np.mean(tip_distances)
        
        # Più permissivo: < 2.0x hand_size
        threshold = hand_size * 2.0
        if avg_tip_distance < threshold:
            distance_score = 1.0 - (avg_tip_distance / threshold)
            scores.append(distance_score)
        
        # === CRITERIO 3: Punte Raggruppate ===
        inter_tip_distances = []
        for i in range(len(self.finger_tips[1:]) - 1):
            for j in range(i + 1, len(self.finger_tips[1:])):
                dist = self._calculate_distance(
                    landmarks[self.finger_tips[1:][i]], 
                    landmarks[self.finger_tips[1:][j]]
                )
                inter_tip_distances.append(dist)
        
        avg_inter_tip = np.mean(inter_tip_distances)
        
        # Più permissivo: < 0.7x hand_size
        grouping_threshold = hand_size * 0.7
        if avg_inter_tip < grouping_threshold:
            grouping_score = 1.0 - (avg_inter_tip / grouping_threshold)
            scores.append(grouping_score)
        
        # === VALUTAZIONE FINALE (semplificata) ===
        # Serve almeno 2 criteri soddisfatti (invece di 3)
        if len(scores) < 2:
            return False, 0.0
        
        # Confidenza base dalla media
        confidence = np.mean(scores)
        
        # Boost se nessun dito esteso
        if num_extended == 0:
            confidence = min(1.0, confidence + 0.2)
        
        # Soglia minima molto bassa
        if confidence >= 0.3:
            return True, min(0.95, confidence)
        
        return False, 0.0
    
    def recognize_gesture(self, hand_landmarks, frame_shape: Tuple[int, int]) -> Tuple[str, float]:
        """
        Riconosce il gesto della mano con scoring di confidenza migliorato.
        
        Args:
            hand_landmarks: Landmark della mano da MediaPipe
            frame_shape: (height, width) del frame
            
        Returns:
            Tupla (gesto, confidenza) dove confidenza è un valore tra 0.0 e 1.0
        """
        fingers = self.get_finger_states(hand_landmarks, frame_shape)
        if hasattr(hand_landmarks, 'landmark'):
            landmarks = hand_landmarks.landmark
        else:
            landmarks = hand_landmarks
        
        # Conta le dita estese
        extended_count = sum(fingers)
        
        # === GESTI DI GIOCO CON CONFIDENZA ===
        
        # SASSO: Pugno chiuso - controllo multi-criterio avanzato
        is_fist, fist_confidence = self._is_fist_closed(hand_landmarks, fingers)
        if is_fist:
            return 'rock', fist_confidence
        
        # CARTA: Tutte le dita estese (mano aperta)
        if extended_count >= 4:
            # Verifica che le dita siano ben aperte
            confidence = 0.7 + (extended_count - 4) * 0.1  # 0.7-0.8 base
            
            # Bonus se anche il pollice è esteso
            if fingers[0]:
                confidence += 0.15
                
            return 'paper', min(1.0, confidence)
        
        # FORBICE: Solo indice e medio estesi con geometria a V
        if fingers[1] and fingers[2] and not fingers[3] and not fingers[4]:
            # Verifica la separazione tra indice e medio (forma a V)
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            index_mcp = landmarks[5]
            middle_mcp = landmarks[9]
            
            # Distanza tra le punte
            tips_distance = self._calculate_distance(index_tip, middle_tip)
            # Distanza tra le basi
            mcps_distance = self._calculate_distance(index_mcp, middle_mcp)
            
            # Le punte dovrebbero essere più distanti delle basi (forma a V)
            v_ratio = tips_distance / (mcps_distance + 1e-6)
            
            # Confidenza basata sulla qualità della V
            excellent_ratio = GESTURE_DETECTION.get('scissors_v_ratio_excellent', 1.3)
            good_ratio = GESTURE_DETECTION.get('scissors_v_ratio_good', 1.1)
            
            if v_ratio > excellent_ratio:
                confidence = 0.9
            elif v_ratio > good_ratio:
                confidence = 0.75
            else:
                confidence = 0.6
            
            return 'scissors', confidence
        
        return 'none', 0.0
    
    def _apply_temporal_smoothing(self, gesture: str, confidence: float) -> Tuple[str, float]:
        """
        Applica smoothing temporale per ridurre il jitter nel riconoscimento.
        
        Args:
            gesture: Gesto riconosciuto nel frame corrente
            confidence: Confidenza del gesto corrente
            
        Returns:
            Tupla (gesto_smoothed, confidenza_smoothed)
        """
        # Aggiungi alla storia
        self.gesture_history.append(gesture)
        self.confidence_history.append(confidence)
        
        # Se abbiamo pochi campioni, ritorna il gesto corrente
        if len(self.gesture_history) < 3:
            return gesture, confidence
        
        # Conta le occorrenze di ogni gesto
        gesture_counts: Dict[str, int] = {}
        for g in self.gesture_history:
            gesture_counts[g] = gesture_counts.get(g, 0) + 1
        
        # Trova il gesto più frequente
        most_common_gesture = max(gesture_counts, key=gesture_counts.get)
        
        # Calcola confidenza media per il gesto più comune
        confidences = [
            c for g, c in zip(self.gesture_history, self.confidence_history) 
            if g == most_common_gesture
        ]
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Ritorna il gesto più frequente solo se appare nella maggioranza
        majority_threshold = len(self.gesture_history) // 2
        if gesture_counts[most_common_gesture] >= majority_threshold:
            return most_common_gesture, avg_confidence
        
        # Altrimenti ritorna 'none' (nessun gesto stabile)
        return 'none', 0.0
    
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
        self.gesture_history.clear()
        self.confidence_history.clear()
    
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
        if hasattr(hand_landmarks, 'landmark'):
            landmarks = hand_landmarks.landmark
        else:
            landmarks = hand_landmarks
        
        # Usa il palmo (landmark 0) come centro
        palm = landmarks[0]
        return int(palm.x * w), int(palm.y * h)
    
    def release(self):
        """Rilascia le risorse."""
        try:
            if getattr(self, 'use_solutions', False) and hasattr(self, 'hands'):
                try:
                    self.hands.close()
                except Exception:
                    pass
            if getattr(self, 'use_tasks', False) and hasattr(self, 'hand_landmarker'):
                try:
                    self.hand_landmarker.close()
                except Exception:
                    pass
        except Exception:
            pass


class CameraManager:
    """
    Gestisce l'accesso alla webcam.
    """
    
    @staticmethod
    def get_available_cameras(max_cameras: int = 10, timeout_per_camera: float = 2.0) -> list:
        """
        Rileva tutte le camera disponibili nel sistema.
        
        Args:
            max_cameras: Numero massimo di camera da controllare
            timeout_per_camera: Timeout in secondi per ogni camera (non usato direttamente ma per ref)
            
        Returns:
            Lista di tuple (indice, nome) delle camera disponibili
        """
        available = []
        for i in range(max_cameras):
            cap = None
            try:
                cap = cv2.VideoCapture(i)
                if cap is not None and cap.isOpened():
                    # Prova a leggere un frame per verificare che funzioni
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        # Ottieni il nome della camera se disponibile
                        try:
                            backend = cap.getBackendName()
                        except:
                            backend = "Unknown"
                        name = f"Camera {i} ({backend})"
                        available.append((i, name))
            except cv2.error as e:
                # Camera non disponibile o errore OpenCV, continua con la prossima
                pass
            except Exception as e:
                # Errore generico, continua
                print(f"Errore durante scansione camera {i}: {e}")
            finally:
                # Assicurati di rilasciare sempre la camera
                if cap is not None:
                    try:
                        cap.release()
                    except:
                        pass
        return available
    
    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Inizializza la camera.
        
        Args:
            camera_index: Indice della webcam
            width: Larghezza del frame
            height: Altezza del frame
        """
        self.camera_index = camera_index
        self.desired_width = width
        self.desired_height = height
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Impossibile aprire la camera {camera_index}")
        
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.consecutive_failures = 0
        self.max_failures = 10  # Dopo 10 frame falliti, considera la camera disconnessa
    
    def read(self, flip: bool = True) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Legge un frame dalla camera.
        
        Args:
            flip: Se True, specchia il frame orizzontalmente
            
        Returns:
            Tuple (success, frame)
        """
        # Controlla prima se la camera è ancora aperta
        if not self.cap.isOpened():
            self.consecutive_failures = self.max_failures
            return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if ret and frame is not None:
                self.consecutive_failures = 0
                if flip:
                    frame = cv2.flip(frame, 1)
            else:
                self.consecutive_failures += 1
            
            return ret, frame
        except cv2.error as e:
            # Errore OpenCV durante la lettura (es. camera disconnessa)
            print(f"Errore OpenCV durante lettura camera: {e}")
            self.consecutive_failures = self.max_failures
            return False, None
        except Exception as e:
            # Errore generico
            print(f"Errore imprevisto durante lettura camera: {e}")
            self.consecutive_failures += 1
            return False, None
    
    def is_disconnected(self) -> bool:
        """Verifica se la camera sembra essere disconnessa."""
        return self.consecutive_failures >= self.max_failures or not self.cap.isOpened()
    
    def switch_camera(self, new_index: int) -> bool:
        """
        Cambia la camera attiva.
        
        Args:
            new_index: Indice della nuova camera
            
        Returns:
            True se il cambio è riuscito, False altrimenti
        """
        try:
            # Rilascia la camera attuale in modo sicuro
            if self.cap is not None:
                try:
                    self.cap.release()
                except:
                    pass
            
            # Prova ad aprire la nuova camera
            self.cap = cv2.VideoCapture(new_index)
            if self.cap is None:
                return False
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.desired_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.desired_height)
            
            if self.cap.isOpened():
                # Verifica che la camera funzioni leggendo un frame
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.camera_index = new_index
                    self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    self.consecutive_failures = 0
                    return True
            
            return False
        except Exception as e:
            print(f"Errore durante switch camera a indice {new_index}: {e}")
            return False
    
    def try_reconnect(self) -> bool:
        """
        Prova a riconnettere la camera attuale.
        
        Returns:
            True se la riconnessione è riuscita, False altrimenti
        """
        try:
            # Reset failure count before trying
            self.consecutive_failures = 0
            return self.switch_camera(self.camera_index)
        except Exception as e:
            print(f"Errore durante tentativo di riconnessione camera: {e}")
            return False
    
    def get_health_status(self) -> dict:
        """
        Restituisce lo stato di salute della camera.
        
        Returns:
            Dizionario con informazioni sullo stato della camera
        """
        return {
            'is_opened': self.cap.isOpened() if self.cap else False,
            'consecutive_failures': self.consecutive_failures,
            'is_disconnected': self.is_disconnected(),
            'camera_index': self.camera_index,
            'health_percent': max(0, 100 - (self.consecutive_failures * 10))
        }
    
    def release(self):
        """Rilascia la camera in modo sicuro."""
        try:
            if self.cap is not None:
                self.cap.release()
        except Exception as e:
            print(f"Errore durante rilascio camera: {e}")
        finally:
            self.consecutive_failures = self.max_failures
    
    def is_opened(self) -> bool:
        """Verifica se la camera e' aperta."""
        try:
            return self.cap is not None and self.cap.isOpened()
        except:
            return False
