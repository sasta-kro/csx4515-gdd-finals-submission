using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Sumo
{
    public class PlayerDeath : MonoBehaviour
    {
        public GameManager GameManager;

        private static readonly float _lowerBound = -5.0f;


        void Update()
        {
            if (Time.timeScale == 0f) return;

            if (_lowerBound > transform.position.y)
            {
                Debug.Log("Game Over!");
                Destroy(gameObject);
                GameManager.GameOver = true;
            }
        }
    }
}
