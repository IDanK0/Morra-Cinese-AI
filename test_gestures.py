"""
Script di test per il sistema di riconoscimento gesti migliorato
Esegui questo script per testare i miglioramenti senza avviare il gioco completo
"""

import cv2
import time
from gesture.hand_detector import HandDetector, CameraManager

# Questo file è un test interattivo per uso manuale. Evita che pytest lo raccolga
import pytest
pytest.skip("Interactive gesture tests - skip during automated pytest run", allow_module_level=True)

def test_gesture_recognition():
    """Test interattivo del riconoscimento gesti."""
    print("=" * 60)
    print("  TEST SISTEMA RICONOSCIMENTO GESTI MIGLIORATO")
    print("=" * 60)
    print()
    print("Istruzioni:")
    print("1. Testa SASSO (pugno chiuso)")
    print("2. Testa CARTA (mano aperta, 5 dita)")
    print("3. Testa FORBICI (V con indice e medio)")
    print("4. Testa gesti di navigazione (indice direzionale)")
    print()
    print("Premi 'q' per uscire")
    print("Premi 's' per screenshot")
    print("-" * 60)
    
    try:
        # Inizializza camera
        camera = CameraManager(camera_index=0, width=640, height=480)
        print("✓ Camera inizializzata")
        
        # Inizializza hand detector con parametri migliorati
        hand_detector = HandDetector(
            max_hands=1,
            detection_confidence=0.7,
            tracking_confidence=0.7
        )
        print("✓ Hand Detector inizializzato")
        print()
        
        # Contatori per statistiche
        frame_count = 0
        gesture_counts = {
            'rock': 0,
            'paper': 0,
            'scissors': 0,
            'point_up': 0,
            'point_down': 0,
            'point_left': 0,
            'point_right': 0,
            'thumbs_up': 0,
            'none': 0
        }
        
        confidence_sum = {k: 0.0 for k in gesture_counts.keys()}
        
        last_gesture = None
        gesture_stable_frames = 0
        
        while True:
            ret, frame = camera.read(flip=True)
            if not ret:
                print("Errore nella lettura del frame")
                break
            
            frame_count += 1
            
            # Rileva mani
            processed_frame, hands = hand_detector.find_hands(frame, draw=True)
            
            if hands:
                hand = hands[0]
                
                # Riconosci gesto con confidenza
                gesture, confidence = hand_detector.recognize_gesture(
                    hand['landmarks'],
                    frame.shape
                )
                
                # Applica smoothing temporale
                smooth_gesture, smooth_confidence = hand_detector._apply_temporal_smoothing(
                    gesture, confidence
                )
                
                # Statistiche
                if smooth_gesture in gesture_counts:
                    gesture_counts[smooth_gesture] += 1
                    confidence_sum[smooth_gesture] += smooth_confidence
                
                # Verifica stabilità
                if smooth_gesture == last_gesture and smooth_gesture != 'none':
                    gesture_stable_frames += 1
                else:
                    gesture_stable_frames = 0
                    last_gesture = smooth_gesture
                
                # Visualizza info sul frame
                y_offset = 30
                
                # Gesto corrente (raw)
                cv2.putText(
                    processed_frame,
                    f"Gesto RAW: {gesture}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2
                )
                y_offset += 30
                
                # Confidenza raw
                cv2.putText(
                    processed_frame,
                    f"Confidenza RAW: {confidence:.2f}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 255),
                    2
                )
                y_offset += 30
                
                # Gesto smoothed
                color = (0, 255, 0) if smooth_gesture != 'none' else (100, 100, 100)
                cv2.putText(
                    processed_frame,
                    f"Gesto SMOOTHED: {smooth_gesture}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )
                y_offset += 30
                
                # Confidenza smoothed
                cv2.putText(
                    processed_frame,
                    f"Confidenza SMOOTH: {smooth_confidence:.2f}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )
                y_offset += 30
                
                # Stabilità
                stability_color = (0, 255, 0) if gesture_stable_frames > 5 else (0, 165, 255)
                cv2.putText(
                    processed_frame,
                    f"Stabilita: {gesture_stable_frames} frames",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    stability_color,
                    2
                )
                y_offset += 30
                
                # Stato dita (debug)
                fingers = hand_detector.get_finger_states(
                    hand['landmarks'],
                    frame.shape
                )
                fingers_str = "".join(["1" if f else "0" for f in fingers])
                cv2.putText(
                    processed_frame,
                    f"Dita [P I M A M]: {fingers_str}",
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (200, 200, 200),
                    1
                )
                
            else:
                # Nessuna mano rilevata
                cv2.putText(
                    processed_frame,
                    "Nessuna mano rilevata",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )
                hand_detector.reset_gesture_tracking()
                last_gesture = None
                gesture_stable_frames = 0
            
            # Info generale
            cv2.putText(
                processed_frame,
                f"Frame: {frame_count}",
                (10, frame.shape[0] - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )
            
            cv2.putText(
                processed_frame,
                "Premi 'q' per uscire | 's' per screenshot",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1
            )
            
            # Mostra frame
            cv2.imshow('Test Riconoscimento Gesti', processed_frame)
            
            # Gestione tasti
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"screenshot_{int(time.time())}.png"
                cv2.imwrite(filename, processed_frame)
                print(f"Screenshot salvato: {filename}")
        
        # Stampa statistiche finali
        print()
        print("=" * 60)
        print("  STATISTICHE TEST")
        print("=" * 60)
        print(f"Frame totali processati: {frame_count}")
        print()
        print("Gesti riconosciuti:")
        for gesture, count in gesture_counts.items():
            if count > 0:
                avg_confidence = confidence_sum[gesture] / count
                percentage = (count / frame_count) * 100
                print(f"  {gesture:15s}: {count:5d} frame ({percentage:5.1f}%) - Conf.media: {avg_confidence:.2f}")
        
        # Cleanup
        camera.release()
        hand_detector.release()
        cv2.destroyAllWindows()
        
        print()
        print("✓ Test completato")
        
    except Exception as e:
        print(f"✗ Errore durante il test: {e}")
        import traceback
        traceback.print_exc()


def test_specific_gesture(gesture_name: str):
    """Test focalizzato su un gesto specifico."""
    print(f"Test specifico per gesto: {gesture_name}")
    print("Mantieni il gesto per 5 secondi...")
    
    try:
        camera = CameraManager(camera_index=0, width=640, height=480)
        hand_detector = HandDetector(max_hands=1)
        
        start_time = time.time()
        samples = []
        
        while time.time() - start_time < 5.0:
            ret, frame = camera.read(flip=True)
            if not ret:
                continue
            
            processed_frame, hands = hand_detector.find_hands(frame, draw=True)
            
            if hands:
                hand = hands[0]
                gesture, confidence = hand_detector.recognize_gesture(
                    hand['landmarks'],
                    frame.shape
                )
                
                if gesture == gesture_name:
                    samples.append(confidence)
            
            cv2.imshow('Test Specifico', processed_frame)
            cv2.waitKey(1)
        
        camera.release()
        hand_detector.release()
        cv2.destroyAllWindows()
        
        if samples:
            print(f"Campioni raccolti: {len(samples)}")
            print(f"Confidenza media: {sum(samples)/len(samples):.2f}")
            print(f"Confidenza min: {min(samples):.2f}")
            print(f"Confidenza max: {max(samples):.2f}")
        else:
            print("Nessun campione raccolto - gesto non riconosciuto")
            
    except Exception as e:
        print(f"Errore: {e}")


if __name__ == "__main__":
    print()
    print("Seleziona modalità test:")
    print("1. Test interattivo completo")
    print("2. Test specifico SASSO")
    print("3. Test specifico CARTA")
    print("4. Test specifico FORBICI")
    print()
    
    choice = input("Scelta (1-4): ").strip()
    
    if choice == '1':
        test_gesture_recognition()
    elif choice == '2':
        test_specific_gesture('rock')
    elif choice == '3':
        test_specific_gesture('paper')
    elif choice == '4':
        test_specific_gesture('scissors')
    else:
        print("Scelta non valida")
