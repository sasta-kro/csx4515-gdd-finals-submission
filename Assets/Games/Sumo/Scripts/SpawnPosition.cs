using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace ThreeInOne.Sumo
{
    public class SpawnPosition
    {
        private static readonly float _spawnRange = 9;


        public static Vector3 Generate()
        {
            float spawnPosX = Random.Range(-_spawnRange, _spawnRange);
            float spawnPosZ = Random.Range(-_spawnRange, _spawnRange);

            return new(spawnPosX, 0, spawnPosZ);
        }
    }
}
