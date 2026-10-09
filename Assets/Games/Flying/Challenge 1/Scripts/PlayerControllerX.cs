using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Flying
{
    public class PlayerControllerX : MonoBehaviour
    {
        public float speed = 18.0f;
        public float rotationSpeed = 8.0f;
        private float verticalInput;
        // Start is called before the first frame update
        void Start()
        {

        }

        // Update is called once per frame
        void Update()
        {
            if (Time.timeScale == 0f) return;

        // Get the player's vertical input
        verticalInput = Input.GetAxis("Vertical");
        // Move the plane forward continuously
        transform.Translate(Vector3.forward * speed * Time.deltaTime);

        // Tilt the plane only when there is input
        transform.Rotate(Vector3.right * rotationSpeed * verticalInput * Time.deltaTime);
        }
    }
}
