using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GameOver : MonoBehaviour
{
    void Start() {
        gameObject.SetActive(false);
    }

    public void Display() {
        gameObject.SetActive(true);
    }
}
