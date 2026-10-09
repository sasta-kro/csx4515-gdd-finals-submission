using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Driving
{
    public class FollowPlayer : MonoBehaviour
    {
        public GameObject Player;
        public Vector3 Offset = new Vector3(0, 5, -7);


        void Start()
        {
            
        }


        void LateUpdate()
        {
            if (Time.timeScale == 0f) return;

            transform.position = Player.transform.position + Offset;
        }
    }
}
