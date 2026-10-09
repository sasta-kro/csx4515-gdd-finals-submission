using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace ThreeInOne.Menus
{
    public sealed class GameMenuController : MonoBehaviour
    {
        [SerializeField] private GameObject pauseCanvas;
        [SerializeField] private GameObject hudCanvas;
        [SerializeField] private GameObject firstSelected;
        [SerializeField] private Text controlsText;

        private bool paused;

        private void Awake()
        {
            var font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            foreach (var label in GetComponentsInChildren<Text>(true))
                label.font = font;
        }

        private void Start()
        {
            switch (SceneManager.GetActiveScene().name)
            {
                case "Driving":
                    controlsText.text = "DRIVING   |   W/S or Up/Down: drive   |   A/D or Left/Right: steer   |   C: camera";
                    break;
                case "Flying":
                    controlsText.text = "FLYING   |   W/S or Up/Down: pitch the plane";
                    break;
                case "Sumo":
                    controlsText.text = "SUMO   |   W/S or Up/Down: roll   |   A/D or Left/Right: rotate view   |   Collect powerups";
                    break;
            }

            SetPaused(false);
        }

        private void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape))
                SetPaused(!paused);
        }

        public void PauseGame() => SetPaused(true);
        public void ResumeGame() => SetPaused(false);

        public void RestartGame()
        {
            SetPaused(false);
            SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex);
        }

        public void BackToMainMenu()
        {
            SetPaused(false);
            SceneManager.LoadScene("MainMenu");
        }

        private void SetPaused(bool value)
        {
            paused = value;
            Time.timeScale = value ? 0f : 1f;
            AudioListener.pause = value;
            pauseCanvas.SetActive(value);
            hudCanvas.SetActive(!value);
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;

            if (EventSystem.current != null)
                EventSystem.current.SetSelectedGameObject(value ? firstSelected : null);
        }

        private void OnDestroy()
        {
            Time.timeScale = 1f;
            AudioListener.pause = false;
        }
    }
}
