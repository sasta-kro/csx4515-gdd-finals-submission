using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Flying
{
    public class FollowPlayerX : MonoBehaviour
    {
        public GameObject player;
        private Vector3 offset;

        // Start is called before the first frame update
        void Start()
        {
            offset = new Vector3(25, 5, -5);
        }

        // Update is called once per frame
        void LateUpdate()
        {
            if (Time.timeScale == 0f) return;

            transform.position = player.transform.position + offset;
        }
    }
}
