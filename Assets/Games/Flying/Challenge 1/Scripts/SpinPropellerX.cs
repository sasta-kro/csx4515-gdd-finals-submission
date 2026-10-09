using UnityEngine;

namespace ThreeInOne.Flying
{
    public class SpinPropellerX : MonoBehaviour
    {
        public float spinSpeed = 1000f;

        void Update()
        {
            if (Time.timeScale == 0f) return;

            transform.Rotate(Vector3.forward * spinSpeed * Time.deltaTime);
        }
    }
}
