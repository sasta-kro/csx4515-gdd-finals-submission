using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Driving
{
    public class TrafficMove : MonoBehaviour
    {
        void Update()
        {
            if (Time.timeScale == 0f) return;

            transform.Translate(Vector3.forward * (1.8f * Time.deltaTime));
        }
    }
}
