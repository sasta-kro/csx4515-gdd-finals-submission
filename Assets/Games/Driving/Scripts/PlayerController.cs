using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Driving
{
    public class PlayerController : MonoBehaviour
    {
        private float _speed = 20.0f;
        private float _turnSpeed = 45.0f;


        void Start()
        {
            
        }


        void Update()
        {
            if (Time.timeScale == 0f) return;

            float forwardInput = Input.GetAxis("Vertical");
            float horizontalInput = Input.GetAxis("Horizontal");

            transform.Translate(Vector3.forward * Time.deltaTime * _speed * forwardInput);
            transform.Rotate(Vector3.up, Time.deltaTime * _turnSpeed * horizontalInput);
        }
    }
}
