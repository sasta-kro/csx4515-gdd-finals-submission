using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

namespace ThreeInOne.Menus
{
    public sealed class MainMenuController : MonoBehaviour
    {
        [SerializeField] private GameObject firstSelected;

        private void Awake()
        {
            var font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            foreach (var label in GetComponentsInChildren<Text>(true))
                label.font = font;
        }

        private void Start()
        {
            Time.timeScale = 1f;
            AudioListener.pause = false;
            Cursor.lockState = CursorLockMode.None;
            Cursor.visible = true;
            EventSystem.current.SetSelectedGameObject(firstSelected);
        }

        public void PlayDriving() => SceneManager.LoadScene("Driving");
        public void PlayFlying() => SceneManager.LoadScene("Flying");
        public void PlaySumo() => SceneManager.LoadScene("Sumo");

        public void ExitGame()
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }
    }
}
