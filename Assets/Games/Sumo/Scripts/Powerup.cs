using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Sumo
{
    public enum PowerType
    {
        Superpower,
        Projectiles,
        Smash
    };

    public class Powerup : MonoBehaviour
    {
        public PowerType PowerType;
    }
}
