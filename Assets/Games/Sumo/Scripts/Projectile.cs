using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Sumo
{
    public class Projectile : MonoBehaviour
    {
        private static readonly float _forceFactor = 30.0f;


        private void OnTriggerEnter(Collider other)
        {
            if (other.CompareTag("Enemy"))
            {
                Destroy(gameObject);

                var enemyRigdbody = other.GetComponent<Rigidbody>();
                var moveForward = GetComponent<MoveForward>();
                var lookDirection = moveForward.LookDirection;
                enemyRigdbody.AddForce(lookDirection * _forceFactor, ForceMode.Impulse);
            }
        }
    }
}
