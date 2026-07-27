window.DEMO_DATA={
 "outcome_colors": {
  "identified": "#2ecc71",
  "abstracted": "#f39c12",
  "unknown": "#e74c3c",
  "rejected": "#7f8c8d"
 },
 "seg_marks": {
  "confirm": "\u2713",
  "neutral": "\u223c",
  "flag": "\u26a0",
  "conflict": "\u2717",
  "off": ""
 },
 "seg_legend": [
  {
   "name": "road",
   "color": "#804080"
  },
  {
   "name": "sidewalk",
   "color": "#f423e8"
  },
  {
   "name": "building",
   "color": "#464646"
  },
  {
   "name": "vegetation",
   "color": "#6b8e23"
  },
  {
   "name": "terrain",
   "color": "#98fb98"
  },
  {
   "name": "sky",
   "color": "#4682b4"
  },
  {
   "name": "person",
   "color": "#dc143c"
  },
  {
   "name": "animal",
   "color": "#ff8c00"
  },
  {
   "name": "vehicle",
   "color": "#00008e"
  },
  {
   "name": "two_wheeler",
   "color": "#770b20"
  },
  {
   "name": "pole",
   "color": "#999999"
  },
  {
   "name": "traffic_sign",
   "color": "#dcdc00"
  }
 ],
 "taxonomy": {
  "name": "Object",
  "floor": false,
  "children": [
   {
    "name": "Moving Object",
    "floor": false,
    "children": [
     {
      "name": "Living Being",
      "floor": true,
      "children": [
       {
        "name": "Person",
        "floor": false,
        "children": [
         {
          "name": "Pedestrian",
          "floor": false,
          "children": []
         },
         {
          "name": "Rider",
          "floor": false,
          "children": []
         }
        ]
       },
       {
        "name": "Animal",
        "floor": false,
        "children": [
         {
          "name": "Dog",
          "floor": false,
          "children": []
         },
         {
          "name": "Cat",
          "floor": false,
          "children": []
         },
         {
          "name": "Horse",
          "floor": false,
          "children": []
         },
         {
          "name": "Large Livestock",
          "floor": false,
          "children": []
         },
         {
          "name": "Bird",
          "floor": false,
          "children": []
         }
        ]
       }
      ]
     },
     {
      "name": "Vehicle",
      "floor": true,
      "children": [
       {
        "name": "Two-Wheeler",
        "floor": false,
        "children": [
         {
          "name": "Bicycle",
          "floor": false,
          "children": []
         },
         {
          "name": "Motorcycle",
          "floor": false,
          "children": []
         }
        ]
       },
       {
        "name": "Road Vehicle",
        "floor": false,
        "children": [
         {
          "name": "Passenger Car",
          "floor": false,
          "children": [
           {
            "name": "Sedan",
            "floor": false,
            "children": []
           },
           {
            "name": "SUV",
            "floor": false,
            "children": []
           }
          ]
         },
         {
          "name": "Commercial Vehicle",
          "floor": false,
          "children": [
           {
            "name": "Transport Vehicle",
            "floor": false,
            "children": [
             {
              "name": "Truck",
              "floor": false,
              "children": [
               {
                "name": "Heavy Truck",
                "floor": false,
                "children": [
                 {
                  "name": "MAN Truck",
                  "floor": false,
                  "children": []
                 }
                ]
               }
              ]
             },
             {
              "name": "Bus",
              "floor": false,
              "children": []
             }
            ]
           }
          ]
         }
        ]
       },
       {
        "name": "Rail Vehicle",
        "floor": false,
        "children": [
         {
          "name": "Train",
          "floor": false,
          "children": []
         }
        ]
       }
      ]
     }
    ]
   },
   {
    "name": "Static Object",
    "floor": true,
    "children": [
     {
      "name": "Traffic Infrastructure",
      "floor": false,
      "children": [
       {
        "name": "Traffic Light",
        "floor": false,
        "children": []
       },
       {
        "name": "Traffic Sign",
        "floor": false,
        "children": []
       },
       {
        "name": "Traffic Cone",
        "floor": false,
        "children": []
       }
      ]
     },
     {
      "name": "Roadside Object",
      "floor": false,
      "children": [
       {
        "name": "Bench",
        "floor": false,
        "children": []
       },
       {
        "name": "Fire Hydrant",
        "floor": false,
        "children": []
       },
       {
        "name": "Parking Meter",
        "floor": false,
        "children": []
       }
      ]
     }
    ]
   }
  ]
 },
 "scenes": [
  {
   "id": "scene_00",
   "image": "data/scene_00.jpg",
   "seg": "data/scene_00_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      404,
      141,
      742,
      494
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.42,
     "importance": 1.0,
     "yolo": "sheep",
     "yolo_conf": 0.54,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Living Being (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.734,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.425,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.734,
      "Living Being": 0.425,
      "Person": 0.154,
      "Pedestrian": 0.102,
      "Rider": 0.053,
      "Animal": 0.27,
      "Dog": 0.06,
      "Cat": 0.041,
      "Horse": 0.059,
      "Large Livestock": 0.063,
      "Bird": 0.048,
      "Vehicle": 0.309,
      "Two-Wheeler": 0.098,
      "Bicycle": 0.058,
      "Motorcycle": 0.04,
      "Road Vehicle": 0.184,
      "Passenger Car": 0.108,
      "Sedan": 0.056,
      "SUV": 0.052,
      "Commercial Vehicle": 0.075,
      "Transport Vehicle": 0.075,
      "Truck": 0.037,
      "Heavy Truck": 0.037,
      "MAN Truck": 0.037,
      "Bus": 0.038,
      "Rail Vehicle": 0.027,
      "Train": 0.027,
      "Static Object": 0.266,
      "Traffic Infrastructure": 0.165,
      "Traffic Light": 0.047,
      "Traffic Sign": 0.068,
      "Traffic Cone": 0.05,
      "Roadside Object": 0.101,
      "Bench": 0.034,
      "Fire Hydrant": 0.028,
      "Parking Meter": 0.039
     },
     "flat": {
      "leaf": "Pedestrian",
      "prob": 0.1,
      "accepted": false
     }
    }
   ]
  },
  {
   "id": "scene_01",
   "image": "data/scene_01.jpg",
   "seg": "data/scene_01_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      402,
      85,
      692,
      485
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.42,
     "importance": 1.0,
     "yolo": "giraffe",
     "yolo_conf": 0.95,
     "novel": true,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Living Being (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.744,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.419,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.744,
      "Living Being": 0.419,
      "Person": 0.136,
      "Pedestrian": 0.101,
      "Rider": 0.035,
      "Animal": 0.283,
      "Dog": 0.046,
      "Cat": 0.04,
      "Horse": 0.069,
      "Large Livestock": 0.081,
      "Bird": 0.047,
      "Vehicle": 0.325,
      "Two-Wheeler": 0.08,
      "Bicycle": 0.05,
      "Motorcycle": 0.03,
      "Road Vehicle": 0.209,
      "Passenger Car": 0.118,
      "Sedan": 0.048,
      "SUV": 0.069,
      "Commercial Vehicle": 0.091,
      "Transport Vehicle": 0.091,
      "Truck": 0.04,
      "Heavy Truck": 0.04,
      "MAN Truck": 0.04,
      "Bus": 0.051,
      "Rail Vehicle": 0.037,
      "Train": 0.037,
      "Static Object": 0.256,
      "Traffic Infrastructure": 0.145,
      "Traffic Light": 0.041,
      "Traffic Sign": 0.062,
      "Traffic Cone": 0.043,
      "Roadside Object": 0.11,
      "Bench": 0.028,
      "Fire Hydrant": 0.033,
      "Parking Meter": 0.05
     },
     "flat": {
      "leaf": "Pedestrian",
      "prob": 0.1,
      "accepted": false
     }
    }
   ]
  },
  {
   "id": "scene_02",
   "image": "data/scene_02.jpg",
   "seg": "data/scene_02_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      410,
      39,
      680,
      468
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.41,
     "importance": 1.0,
     "yolo": "giraffe",
     "yolo_conf": 0.95,
     "novel": true,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Living Being (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.719,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.406,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.719,
      "Living Being": 0.406,
      "Person": 0.124,
      "Pedestrian": 0.095,
      "Rider": 0.03,
      "Animal": 0.282,
      "Dog": 0.053,
      "Cat": 0.045,
      "Horse": 0.066,
      "Large Livestock": 0.066,
      "Bird": 0.052,
      "Vehicle": 0.312,
      "Two-Wheeler": 0.08,
      "Bicycle": 0.047,
      "Motorcycle": 0.034,
      "Road Vehicle": 0.191,
      "Passenger Car": 0.098,
      "Sedan": 0.044,
      "SUV": 0.054,
      "Commercial Vehicle": 0.093,
      "Transport Vehicle": 0.093,
      "Truck": 0.04,
      "Heavy Truck": 0.04,
      "MAN Truck": 0.04,
      "Bus": 0.053,
      "Rail Vehicle": 0.041,
      "Train": 0.041,
      "Static Object": 0.281,
      "Traffic Infrastructure": 0.165,
      "Traffic Light": 0.053,
      "Traffic Sign": 0.068,
      "Traffic Cone": 0.043,
      "Roadside Object": 0.117,
      "Bench": 0.029,
      "Fire Hydrant": 0.037,
      "Parking Meter": 0.05
     },
     "flat": {
      "leaf": "Pedestrian",
      "prob": 0.09,
      "accepted": false
     }
    },
    {
     "box": [
      265,
      292,
      278,
      316
     ],
     "label": "UNKNOWN OBSTACLE (~Moving Object)",
     "outcome": "unknown",
     "confidence": 0.67,
     "importance": 0.05,
     "yolo": "person",
     "yolo_conf": 0.72,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "unverifiable (dominant context: terrain)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.671,
       "floor": false
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.671,
      "Living Being": 0.368,
      "Person": 0.103,
      "Pedestrian": 0.047,
      "Rider": 0.056,
      "Animal": 0.265,
      "Dog": 0.054,
      "Cat": 0.044,
      "Horse": 0.05,
      "Large Livestock": 0.06,
      "Bird": 0.056,
      "Vehicle": 0.303,
      "Two-Wheeler": 0.113,
      "Bicycle": 0.06,
      "Motorcycle": 0.053,
      "Road Vehicle": 0.145,
      "Passenger Car": 0.07,
      "Sedan": 0.04,
      "SUV": 0.029,
      "Commercial Vehicle": 0.075,
      "Transport Vehicle": 0.075,
      "Truck": 0.034,
      "Heavy Truck": 0.034,
      "MAN Truck": 0.034,
      "Bus": 0.041,
      "Rail Vehicle": 0.045,
      "Train": 0.045,
      "Static Object": 0.329,
      "Traffic Infrastructure": 0.149,
      "Traffic Light": 0.051,
      "Traffic Sign": 0.055,
      "Traffic Cone": 0.042,
      "Roadside Object": 0.18,
      "Bench": 0.044,
      "Fire Hydrant": 0.084,
      "Parking Meter": 0.053
     },
     "flat": {
      "leaf": "Fire Hydrant",
      "prob": 0.08,
      "accepted": false
     }
    }
   ]
  },
  {
   "id": "scene_03",
   "image": "data/scene_03.jpg",
   "seg": "data/scene_03_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      195,
      118,
      823,
      451
     ],
     "label": "Vehicle",
     "outcome": "abstracted",
     "confidence": 0.41,
     "importance": 1.0,
     "yolo": "airplane",
     "yolo_conf": 0.59,
     "novel": true,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Vehicle (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.805,
       "floor": false
      },
      {
       "name": "Vehicle",
       "mass": 0.413,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.805,
      "Living Being": 0.392,
      "Person": 0.104,
      "Pedestrian": 0.047,
      "Rider": 0.057,
      "Animal": 0.288,
      "Dog": 0.047,
      "Cat": 0.051,
      "Horse": 0.053,
      "Large Livestock": 0.066,
      "Bird": 0.072,
      "Vehicle": 0.413,
      "Two-Wheeler": 0.115,
      "Bicycle": 0.05,
      "Motorcycle": 0.065,
      "Road Vehicle": 0.256,
      "Passenger Car": 0.153,
      "Sedan": 0.077,
      "SUV": 0.075,
      "Commercial Vehicle": 0.103,
      "Transport Vehicle": 0.103,
      "Truck": 0.055,
      "Heavy Truck": 0.055,
      "MAN Truck": 0.055,
      "Bus": 0.048,
      "Rail Vehicle": 0.042,
      "Train": 0.042,
      "Static Object": 0.195,
      "Traffic Infrastructure": 0.098,
      "Traffic Light": 0.033,
      "Traffic Sign": 0.036,
      "Traffic Cone": 0.03,
      "Roadside Object": 0.097,
      "Bench": 0.028,
      "Fire Hydrant": 0.028,
      "Parking Meter": 0.041
     },
     "flat": {
      "leaf": "Sedan",
      "prob": 0.08,
      "accepted": false
     }
    },
    {
     "box": [
      445,
      200,
      467,
      222
     ],
     "label": "UNKNOWN OBSTACLE (~Moving Object)",
     "outcome": "unknown",
     "confidence": 0.66,
     "importance": 0.07,
     "yolo": "person",
     "yolo_conf": 0.23,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "unverifiable (dominant context: two_wheeler)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.656,
       "floor": false
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.656,
      "Living Being": 0.353,
      "Person": 0.091,
      "Pedestrian": 0.039,
      "Rider": 0.052,
      "Animal": 0.262,
      "Dog": 0.05,
      "Cat": 0.046,
      "Horse": 0.048,
      "Large Livestock": 0.059,
      "Bird": 0.059,
      "Vehicle": 0.302,
      "Two-Wheeler": 0.097,
      "Bicycle": 0.047,
      "Motorcycle": 0.05,
      "Road Vehicle": 0.163,
      "Passenger Car": 0.08,
      "Sedan": 0.044,
      "SUV": 0.036,
      "Commercial Vehicle": 0.084,
      "Transport Vehicle": 0.084,
      "Truck": 0.044,
      "Heavy Truck": 0.044,
      "MAN Truck": 0.044,
      "Bus": 0.04,
      "Rail Vehicle": 0.042,
      "Train": 0.042,
      "Static Object": 0.344,
      "Traffic Infrastructure": 0.169,
      "Traffic Light": 0.054,
      "Traffic Sign": 0.048,
      "Traffic Cone": 0.066,
      "Roadside Object": 0.175,
      "Bench": 0.044,
      "Fire Hydrant": 0.077,
      "Parking Meter": 0.055
     },
     "flat": {
      "leaf": "Fire Hydrant",
      "prob": 0.08,
      "accepted": false
     }
    }
   ]
  },
  {
   "id": "scene_04",
   "image": "data/scene_04.jpg",
   "seg": "data/scene_04_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      161,
      41,
      840,
      480
     ],
     "label": "Vehicle",
     "outcome": "abstracted",
     "confidence": 0.44,
     "importance": 1.0,
     "yolo": "truck",
     "yolo_conf": 0.72,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Vehicle (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.786,
       "floor": false
      },
      {
       "name": "Vehicle",
       "mass": 0.442,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.786,
      "Living Being": 0.345,
      "Person": 0.074,
      "Pedestrian": 0.037,
      "Rider": 0.037,
      "Animal": 0.27,
      "Dog": 0.037,
      "Cat": 0.029,
      "Horse": 0.077,
      "Large Livestock": 0.102,
      "Bird": 0.026,
      "Vehicle": 0.442,
      "Two-Wheeler": 0.079,
      "Bicycle": 0.037,
      "Motorcycle": 0.042,
      "Road Vehicle": 0.314,
      "Passenger Car": 0.122,
      "Sedan": 0.068,
      "SUV": 0.054,
      "Commercial Vehicle": 0.192,
      "Transport Vehicle": 0.192,
      "Truck": 0.09,
      "Heavy Truck": 0.09,
      "MAN Truck": 0.09,
      "Bus": 0.102,
      "Rail Vehicle": 0.049,
      "Train": 0.049,
      "Static Object": 0.213,
      "Traffic Infrastructure": 0.13,
      "Traffic Light": 0.038,
      "Traffic Sign": 0.039,
      "Traffic Cone": 0.052,
      "Roadside Object": 0.084,
      "Bench": 0.021,
      "Fire Hydrant": 0.03,
      "Parking Meter": 0.032
     },
     "flat": {
      "leaf": "Bus",
      "prob": 0.1,
      "accepted": false
     }
    },
    {
     "box": [
      170,
      217,
      204,
      236
     ],
     "label": "UNKNOWN OBSTACLE (~Moving Object)",
     "outcome": "unknown",
     "confidence": 0.7,
     "importance": 0.08,
     "yolo": "car",
     "yolo_conf": 0.34,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "unverifiable (dominant context: building)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.702,
       "floor": false
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.702,
      "Living Being": 0.306,
      "Person": 0.107,
      "Pedestrian": 0.05,
      "Rider": 0.057,
      "Animal": 0.199,
      "Dog": 0.042,
      "Cat": 0.035,
      "Horse": 0.036,
      "Large Livestock": 0.048,
      "Bird": 0.037,
      "Vehicle": 0.396,
      "Two-Wheeler": 0.087,
      "Bicycle": 0.041,
      "Motorcycle": 0.045,
      "Road Vehicle": 0.272,
      "Passenger Car": 0.175,
      "Sedan": 0.095,
      "SUV": 0.079,
      "Commercial Vehicle": 0.097,
      "Transport Vehicle": 0.097,
      "Truck": 0.054,
      "Heavy Truck": 0.054,
      "MAN Truck": 0.054,
      "Bus": 0.043,
      "Rail Vehicle": 0.038,
      "Train": 0.038,
      "Static Object": 0.298,
      "Traffic Infrastructure": 0.178,
      "Traffic Light": 0.049,
      "Traffic Sign": 0.062,
      "Traffic Cone": 0.067,
      "Roadside Object": 0.12,
      "Bench": 0.031,
      "Fire Hydrant": 0.04,
      "Parking Meter": 0.049
     },
     "flat": {
      "leaf": "Sedan",
      "prob": 0.1,
      "accepted": false
     }
    },
    {
     "box": [
      7,
      214,
      44,
      242
     ],
     "label": "Vehicle",
     "outcome": "abstracted",
     "confidence": 0.41,
     "importance": 0.09,
     "yolo": "car",
     "yolo_conf": 0.33,
     "novel": false,
     "rejected": true,
     "constraints": "too small for Vehicle (0.0022<0.003)",
     "seg_status": "flag",
     "seg_note": "paths disagree: box says Vehicle, segmentation says 'Static Object' (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.715,
       "floor": false
      },
      {
       "name": "Vehicle",
       "mass": 0.413,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.715,
      "Living Being": 0.302,
      "Person": 0.1,
      "Pedestrian": 0.051,
      "Rider": 0.049,
      "Animal": 0.202,
      "Dog": 0.043,
      "Cat": 0.035,
      "Horse": 0.04,
      "Large Livestock": 0.046,
      "Bird": 0.038,
      "Vehicle": 0.413,
      "Two-Wheeler": 0.084,
      "Bicycle": 0.041,
      "Motorcycle": 0.043,
      "Road Vehicle": 0.29,
      "Passenger Car": 0.151,
      "Sedan": 0.078,
      "SUV": 0.073,
      "Commercial Vehicle": 0.139,
      "Transport Vehicle": 0.139,
      "Truck": 0.083,
      "Heavy Truck": 0.083,
      "MAN Truck": 0.083,
      "Bus": 0.056,
      "Rail Vehicle": 0.038,
      "Train": 0.038,
      "Static Object": 0.285,
      "Traffic Infrastructure": 0.148,
      "Traffic Light": 0.042,
      "Traffic Sign": 0.056,
      "Traffic Cone": 0.05,
      "Roadside Object": 0.137,
      "Bench": 0.04,
      "Fire Hydrant": 0.038,
      "Parking Meter": 0.059
     },
     "flat": {
      "leaf": "MAN Truck",
      "prob": 0.08,
      "accepted": false
     }
    },
    {
     "box": [
      0,
      191,
      41,
      242
     ],
     "label": "Vehicle",
     "outcome": "abstracted",
     "confidence": 0.41,
     "importance": 0.14,
     "yolo": "truck",
     "yolo_conf": 0.31,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "flag",
     "seg_note": "paths disagree: box says Vehicle, segmentation says 'Static Object' (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.726,
       "floor": false
      },
      {
       "name": "Vehicle",
       "mass": 0.412,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.726,
      "Living Being": 0.313,
      "Person": 0.095,
      "Pedestrian": 0.045,
      "Rider": 0.049,
      "Animal": 0.219,
      "Dog": 0.042,
      "Cat": 0.045,
      "Horse": 0.044,
      "Large Livestock": 0.045,
      "Bird": 0.043,
      "Vehicle": 0.412,
      "Two-Wheeler": 0.09,
      "Bicycle": 0.04,
      "Motorcycle": 0.05,
      "Road Vehicle": 0.272,
      "Passenger Car": 0.122,
      "Sedan": 0.058,
      "SUV": 0.064,
      "Commercial Vehicle": 0.15,
      "Transport Vehicle": 0.15,
      "Truck": 0.084,
      "Heavy Truck": 0.084,
      "MAN Truck": 0.084,
      "Bus": 0.066,
      "Rail Vehicle": 0.05,
      "Train": 0.05,
      "Static Object": 0.274,
      "Traffic Infrastructure": 0.159,
      "Traffic Light": 0.047,
      "Traffic Sign": 0.053,
      "Traffic Cone": 0.059,
      "Roadside Object": 0.115,
      "Bench": 0.039,
      "Fire Hydrant": 0.026,
      "Parking Meter": 0.05
     },
     "flat": {
      "leaf": "MAN Truck",
      "prob": 0.08,
      "accepted": false
     }
    },
    {
     "box": [
      133,
      216,
      182,
      238
     ],
     "label": "Vehicle",
     "outcome": "abstracted",
     "confidence": 0.43,
     "importance": 0.1,
     "yolo": "car",
     "yolo_conf": 0.31,
     "novel": false,
     "rejected": true,
     "constraints": "too small for Vehicle (0.0024<0.003)",
     "seg_status": "flag",
     "seg_note": "paths disagree: box says Vehicle, segmentation says 'Static Object' (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.694,
       "floor": false
      },
      {
       "name": "Vehicle",
       "mass": 0.432,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.694,
      "Living Being": 0.262,
      "Person": 0.094,
      "Pedestrian": 0.048,
      "Rider": 0.046,
      "Animal": 0.168,
      "Dog": 0.035,
      "Cat": 0.03,
      "Horse": 0.032,
      "Large Livestock": 0.039,
      "Bird": 0.031,
      "Vehicle": 0.432,
      "Two-Wheeler": 0.09,
      "Bicycle": 0.042,
      "Motorcycle": 0.049,
      "Road Vehicle": 0.29,
      "Passenger Car": 0.157,
      "Sedan": 0.086,
      "SUV": 0.071,
      "Commercial Vehicle": 0.134,
      "Transport Vehicle": 0.134,
      "Truck": 0.063,
      "Heavy Truck": 0.063,
      "MAN Truck": 0.063,
      "Bus": 0.071,
      "Rail Vehicle": 0.051,
      "Train": 0.051,
      "Static Object": 0.306,
      "Traffic Infrastructure": 0.185,
      "Traffic Light": 0.066,
      "Traffic Sign": 0.058,
      "Traffic Cone": 0.061,
      "Roadside Object": 0.121,
      "Bench": 0.034,
      "Fire Hydrant": 0.034,
      "Parking Meter": 0.053
     },
     "flat": {
      "leaf": "Sedan",
      "prob": 0.09,
      "accepted": false
     }
    }
   ]
  },
  {
   "id": "scene_05",
   "image": "data/scene_05.jpg",
   "seg": "data/scene_05_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      68,
      273,
      409,
      427
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.47,
     "importance": 0.68,
     "yolo": "dog",
     "yolo_conf": 0.65,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Living Being (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.757,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.465,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.757,
      "Living Being": 0.465,
      "Person": 0.09,
      "Pedestrian": 0.053,
      "Rider": 0.037,
      "Animal": 0.375,
      "Dog": 0.105,
      "Cat": 0.086,
      "Horse": 0.063,
      "Large Livestock": 0.055,
      "Bird": 0.066,
      "Vehicle": 0.292,
      "Two-Wheeler": 0.082,
      "Bicycle": 0.04,
      "Motorcycle": 0.042,
      "Road Vehicle": 0.173,
      "Passenger Car": 0.091,
      "Sedan": 0.036,
      "SUV": 0.056,
      "Commercial Vehicle": 0.081,
      "Transport Vehicle": 0.081,
      "Truck": 0.04,
      "Heavy Truck": 0.04,
      "MAN Truck": 0.04,
      "Bus": 0.042,
      "Rail Vehicle": 0.037,
      "Train": 0.037,
      "Static Object": 0.243,
      "Traffic Infrastructure": 0.137,
      "Traffic Light": 0.043,
      "Traffic Sign": 0.054,
      "Traffic Cone": 0.04,
      "Roadside Object": 0.106,
      "Bench": 0.038,
      "Fire Hydrant": 0.032,
      "Parking Meter": 0.036
     },
     "flat": {
      "leaf": "Dog",
      "prob": 0.11,
      "accepted": false
     }
    }
   ]
  },
  {
   "id": "scene_06",
   "image": "data/scene_06.jpg",
   "seg": "data/scene_06_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      94,
      274,
      242,
      366
     ],
     "label": "Vehicle",
     "outcome": "abstracted",
     "confidence": 0.47,
     "importance": 0.35,
     "yolo": "car",
     "yolo_conf": 0.89,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Vehicle (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.732,
       "floor": false
      },
      {
       "name": "Vehicle",
       "mass": 0.474,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.732,
      "Living Being": 0.258,
      "Person": 0.075,
      "Pedestrian": 0.045,
      "Rider": 0.03,
      "Animal": 0.183,
      "Dog": 0.041,
      "Cat": 0.038,
      "Horse": 0.03,
      "Large Livestock": 0.042,
      "Bird": 0.031,
      "Vehicle": 0.474,
      "Two-Wheeler": 0.071,
      "Bicycle": 0.036,
      "Motorcycle": 0.035,
      "Road Vehicle": 0.37,
      "Passenger Car": 0.267,
      "Sedan": 0.144,
      "SUV": 0.123,
      "Commercial Vehicle": 0.103,
      "Transport Vehicle": 0.103,
      "Truck": 0.059,
      "Heavy Truck": 0.059,
      "MAN Truck": 0.059,
      "Bus": 0.044,
      "Rail Vehicle": 0.033,
      "Train": 0.033,
      "Static Object": 0.268,
      "Traffic Infrastructure": 0.147,
      "Traffic Light": 0.044,
      "Traffic Sign": 0.052,
      "Traffic Cone": 0.051,
      "Roadside Object": 0.121,
      "Bench": 0.027,
      "Fire Hydrant": 0.034,
      "Parking Meter": 0.061
     },
     "flat": {
      "leaf": "Sedan",
      "prob": 0.14,
      "accepted": false
     }
    },
    {
     "box": [
      146,
      172,
      864,
      482
     ],
     "label": "Vehicle",
     "outcome": "abstracted",
     "confidence": 0.48,
     "importance": 1.0,
     "yolo": "truck",
     "yolo_conf": 0.73,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "confirm",
     "seg_note": "segmentation supports Vehicle (99% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.788,
       "floor": false
      },
      {
       "name": "Vehicle",
       "mass": 0.476,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.788,
      "Living Being": 0.312,
      "Person": 0.082,
      "Pedestrian": 0.05,
      "Rider": 0.033,
      "Animal": 0.23,
      "Dog": 0.034,
      "Cat": 0.033,
      "Horse": 0.049,
      "Large Livestock": 0.093,
      "Bird": 0.021,
      "Vehicle": 0.476,
      "Two-Wheeler": 0.085,
      "Bicycle": 0.041,
      "Motorcycle": 0.044,
      "Road Vehicle": 0.346,
      "Passenger Car": 0.189,
      "Sedan": 0.09,
      "SUV": 0.099,
      "Commercial Vehicle": 0.156,
      "Transport Vehicle": 0.156,
      "Truck": 0.095,
      "Heavy Truck": 0.095,
      "MAN Truck": 0.095,
      "Bus": 0.062,
      "Rail Vehicle": 0.045,
      "Train": 0.045,
      "Static Object": 0.212,
      "Traffic Infrastructure": 0.091,
      "Traffic Light": 0.037,
      "Traffic Sign": 0.032,
      "Traffic Cone": 0.021,
      "Roadside Object": 0.121,
      "Bench": 0.038,
      "Fire Hydrant": 0.038,
      "Parking Meter": 0.045
     },
     "flat": {
      "leaf": "SUV",
      "prob": 0.1,
      "accepted": false
     }
    },
    {
     "box": [
      414,
      185,
      475,
      265
     ],
     "label": "UNKNOWN OBSTACLE (~Moving Object)",
     "outcome": "unknown",
     "confidence": 0.7,
     "importance": 0.21,
     "yolo": "person",
     "yolo_conf": 0.64,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "unverifiable (dominant context: vehicle)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.703,
       "floor": false
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.703,
      "Living Being": 0.359,
      "Person": 0.157,
      "Pedestrian": 0.064,
      "Rider": 0.093,
      "Animal": 0.202,
      "Dog": 0.045,
      "Cat": 0.033,
      "Horse": 0.041,
      "Large Livestock": 0.038,
      "Bird": 0.044,
      "Vehicle": 0.344,
      "Two-Wheeler": 0.146,
      "Bicycle": 0.072,
      "Motorcycle": 0.073,
      "Road Vehicle": 0.166,
      "Passenger Car": 0.066,
      "Sedan": 0.035,
      "SUV": 0.031,
      "Commercial Vehicle": 0.1,
      "Transport Vehicle": 0.1,
      "Truck": 0.063,
      "Heavy Truck": 0.063,
      "MAN Truck": 0.063,
      "Bus": 0.037,
      "Rail Vehicle": 0.033,
      "Train": 0.033,
      "Static Object": 0.297,
      "Traffic Infrastructure": 0.127,
      "Traffic Light": 0.049,
      "Traffic Sign": 0.039,
      "Traffic Cone": 0.039,
      "Roadside Object": 0.17,
      "Bench": 0.057,
      "Fire Hydrant": 0.039,
      "Parking Meter": 0.073
     },
     "flat": {
      "leaf": "Rider",
      "prob": 0.09,
      "accepted": false
     }
    },
    {
     "box": [
      498,
      176,
      555,
      269
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.46,
     "importance": 0.22,
     "yolo": "person",
     "yolo_conf": 0.39,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "flag",
     "seg_note": "paths disagree: box says Living Being, segmentation says 'Vehicle' (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.711,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.464,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.711,
      "Living Being": 0.464,
      "Person": 0.182,
      "Pedestrian": 0.106,
      "Rider": 0.077,
      "Animal": 0.281,
      "Dog": 0.056,
      "Cat": 0.042,
      "Horse": 0.069,
      "Large Livestock": 0.066,
      "Bird": 0.049,
      "Vehicle": 0.247,
      "Two-Wheeler": 0.087,
      "Bicycle": 0.049,
      "Motorcycle": 0.039,
      "Road Vehicle": 0.126,
      "Passenger Car": 0.064,
      "Sedan": 0.028,
      "SUV": 0.037,
      "Commercial Vehicle": 0.061,
      "Transport Vehicle": 0.061,
      "Truck": 0.032,
      "Heavy Truck": 0.032,
      "MAN Truck": 0.032,
      "Bus": 0.03,
      "Rail Vehicle": 0.034,
      "Train": 0.034,
      "Static Object": 0.289,
      "Traffic Infrastructure": 0.143,
      "Traffic Light": 0.041,
      "Traffic Sign": 0.054,
      "Traffic Cone": 0.048,
      "Roadside Object": 0.146,
      "Bench": 0.064,
      "Fire Hydrant": 0.034,
      "Parking Meter": 0.048
     },
     "flat": {
      "leaf": "Pedestrian",
      "prob": 0.11,
      "accepted": false
     }
    }
   ]
  },
  {
   "id": "scene_07",
   "image": "data/scene_07.jpg",
   "seg": "data/scene_07_seg.jpg",
   "width": 900,
   "height": 506,
   "caption": "0",
   "detections": [
    {
     "box": [
      371,
      322,
      430,
      375
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.48,
     "importance": 0.16,
     "yolo": "bird",
     "yolo_conf": 0.83,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "weak support for Living Being (0% of box; dominant road)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.783,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.484,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.783,
      "Living Being": 0.484,
      "Person": 0.189,
      "Pedestrian": 0.121,
      "Rider": 0.067,
      "Animal": 0.295,
      "Dog": 0.05,
      "Cat": 0.04,
      "Horse": 0.036,
      "Large Livestock": 0.042,
      "Bird": 0.127,
      "Vehicle": 0.299,
      "Two-Wheeler": 0.088,
      "Bicycle": 0.042,
      "Motorcycle": 0.047,
      "Road Vehicle": 0.183,
      "Passenger Car": 0.109,
      "Sedan": 0.056,
      "SUV": 0.053,
      "Commercial Vehicle": 0.074,
      "Transport Vehicle": 0.074,
      "Truck": 0.048,
      "Heavy Truck": 0.048,
      "MAN Truck": 0.048,
      "Bus": 0.026,
      "Rail Vehicle": 0.028,
      "Train": 0.028,
      "Static Object": 0.217,
      "Traffic Infrastructure": 0.127,
      "Traffic Light": 0.031,
      "Traffic Sign": 0.061,
      "Traffic Cone": 0.034,
      "Roadside Object": 0.09,
      "Bench": 0.025,
      "Fire Hydrant": 0.017,
      "Parking Meter": 0.047
     },
     "flat": {
      "leaf": "Bird",
      "prob": 0.13,
      "accepted": false
     }
    },
    {
     "box": [
      136,
      292,
      210,
      372
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.47,
     "importance": 0.23,
     "yolo": "bird",
     "yolo_conf": 0.79,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "weak support for Living Being (0% of box; dominant road)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.756,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.471,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.756,
      "Living Being": 0.471,
      "Person": 0.216,
      "Pedestrian": 0.157,
      "Rider": 0.059,
      "Animal": 0.255,
      "Dog": 0.041,
      "Cat": 0.035,
      "Horse": 0.028,
      "Large Livestock": 0.039,
      "Bird": 0.111,
      "Vehicle": 0.285,
      "Two-Wheeler": 0.083,
      "Bicycle": 0.036,
      "Motorcycle": 0.046,
      "Road Vehicle": 0.176,
      "Passenger Car": 0.115,
      "Sedan": 0.061,
      "SUV": 0.054,
      "Commercial Vehicle": 0.062,
      "Transport Vehicle": 0.062,
      "Truck": 0.036,
      "Heavy Truck": 0.036,
      "MAN Truck": 0.036,
      "Bus": 0.025,
      "Rail Vehicle": 0.026,
      "Train": 0.026,
      "Static Object": 0.244,
      "Traffic Infrastructure": 0.161,
      "Traffic Light": 0.042,
      "Traffic Sign": 0.068,
      "Traffic Cone": 0.051,
      "Roadside Object": 0.084,
      "Bench": 0.026,
      "Fire Hydrant": 0.015,
      "Parking Meter": 0.043
     },
     "flat": {
      "leaf": "Pedestrian",
      "prob": 0.16,
      "accepted": false
     }
    },
    {
     "box": [
      550,
      328,
      609,
      378
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.5,
     "importance": 0.16,
     "yolo": "bird",
     "yolo_conf": 0.78,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "weak support for Living Being (0% of box; dominant road)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.785,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.498,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.785,
      "Living Being": 0.498,
      "Person": 0.155,
      "Pedestrian": 0.101,
      "Rider": 0.054,
      "Animal": 0.344,
      "Dog": 0.045,
      "Cat": 0.054,
      "Horse": 0.049,
      "Large Livestock": 0.041,
      "Bird": 0.155,
      "Vehicle": 0.287,
      "Two-Wheeler": 0.09,
      "Bicycle": 0.048,
      "Motorcycle": 0.043,
      "Road Vehicle": 0.168,
      "Passenger Car": 0.104,
      "Sedan": 0.06,
      "SUV": 0.044,
      "Commercial Vehicle": 0.064,
      "Transport Vehicle": 0.064,
      "Truck": 0.036,
      "Heavy Truck": 0.036,
      "MAN Truck": 0.036,
      "Bus": 0.028,
      "Rail Vehicle": 0.029,
      "Train": 0.029,
      "Static Object": 0.215,
      "Traffic Infrastructure": 0.108,
      "Traffic Light": 0.026,
      "Traffic Sign": 0.047,
      "Traffic Cone": 0.035,
      "Roadside Object": 0.107,
      "Bench": 0.027,
      "Fire Hydrant": 0.019,
      "Parking Meter": 0.061
     },
     "flat": {
      "leaf": "Bird",
      "prob": 0.16,
      "accepted": false
     }
    },
    {
     "box": [
      264,
      345,
      297,
      379
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.53,
     "importance": 0.1,
     "yolo": "bird",
     "yolo_conf": 0.71,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "weak support for Living Being (0% of box; dominant road)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.797,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.526,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.797,
      "Living Being": 0.526,
      "Person": 0.172,
      "Pedestrian": 0.123,
      "Rider": 0.05,
      "Animal": 0.354,
      "Dog": 0.06,
      "Cat": 0.051,
      "Horse": 0.055,
      "Large Livestock": 0.056,
      "Bird": 0.132,
      "Vehicle": 0.27,
      "Two-Wheeler": 0.088,
      "Bicycle": 0.047,
      "Motorcycle": 0.042,
      "Road Vehicle": 0.149,
      "Passenger Car": 0.083,
      "Sedan": 0.043,
      "SUV": 0.04,
      "Commercial Vehicle": 0.066,
      "Transport Vehicle": 0.066,
      "Truck": 0.036,
      "Heavy Truck": 0.036,
      "MAN Truck": 0.036,
      "Bus": 0.03,
      "Rail Vehicle": 0.033,
      "Train": 0.033,
      "Static Object": 0.203,
      "Traffic Infrastructure": 0.11,
      "Traffic Light": 0.031,
      "Traffic Sign": 0.047,
      "Traffic Cone": 0.031,
      "Roadside Object": 0.093,
      "Bench": 0.029,
      "Fire Hydrant": 0.018,
      "Parking Meter": 0.046
     },
     "flat": {
      "leaf": "Bird",
      "prob": 0.13,
      "accepted": false
     }
    },
    {
     "box": [
      195,
      332,
      256,
      370
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.52,
     "importance": 0.14,
     "yolo": "bird",
     "yolo_conf": 0.7,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "weak support for Living Being (0% of box; dominant road)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.793,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.518,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.793,
      "Living Being": 0.518,
      "Person": 0.17,
      "Pedestrian": 0.108,
      "Rider": 0.062,
      "Animal": 0.347,
      "Dog": 0.059,
      "Cat": 0.049,
      "Horse": 0.051,
      "Large Livestock": 0.058,
      "Bird": 0.13,
      "Vehicle": 0.276,
      "Two-Wheeler": 0.085,
      "Bicycle": 0.043,
      "Motorcycle": 0.042,
      "Road Vehicle": 0.158,
      "Passenger Car": 0.094,
      "Sedan": 0.05,
      "SUV": 0.044,
      "Commercial Vehicle": 0.065,
      "Transport Vehicle": 0.065,
      "Truck": 0.036,
      "Heavy Truck": 0.036,
      "MAN Truck": 0.036,
      "Bus": 0.028,
      "Rail Vehicle": 0.033,
      "Train": 0.033,
      "Static Object": 0.207,
      "Traffic Infrastructure": 0.108,
      "Traffic Light": 0.028,
      "Traffic Sign": 0.045,
      "Traffic Cone": 0.035,
      "Roadside Object": 0.098,
      "Bench": 0.029,
      "Fire Hydrant": 0.021,
      "Parking Meter": 0.048
     },
     "flat": {
      "leaf": "Bird",
      "prob": 0.13,
      "accepted": false
     }
    },
    {
     "box": [
      691,
      338,
      753,
      400
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.49,
     "importance": 0.18,
     "yolo": "bird",
     "yolo_conf": 0.62,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "neutral",
     "seg_note": "weak support for Living Being (0% of box; dominant road)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.775,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.49,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.775,
      "Living Being": 0.49,
      "Person": 0.183,
      "Pedestrian": 0.113,
      "Rider": 0.07,
      "Animal": 0.307,
      "Dog": 0.044,
      "Cat": 0.045,
      "Horse": 0.041,
      "Large Livestock": 0.046,
      "Bird": 0.13,
      "Vehicle": 0.285,
      "Two-Wheeler": 0.097,
      "Bicycle": 0.046,
      "Motorcycle": 0.051,
      "Road Vehicle": 0.162,
      "Passenger Car": 0.086,
      "Sedan": 0.045,
      "SUV": 0.041,
      "Commercial Vehicle": 0.076,
      "Transport Vehicle": 0.076,
      "Truck": 0.044,
      "Heavy Truck": 0.044,
      "MAN Truck": 0.044,
      "Bus": 0.031,
      "Rail Vehicle": 0.026,
      "Train": 0.026,
      "Static Object": 0.225,
      "Traffic Infrastructure": 0.144,
      "Traffic Light": 0.034,
      "Traffic Sign": 0.056,
      "Traffic Cone": 0.053,
      "Roadside Object": 0.081,
      "Bench": 0.022,
      "Fire Hydrant": 0.02,
      "Parking Meter": 0.039
     },
     "flat": {
      "leaf": "Bird",
      "prob": 0.13,
      "accepted": false
     }
    },
    {
     "box": [
      60,
      330,
      103,
      372
     ],
     "label": "Living Being",
     "outcome": "abstracted",
     "confidence": 0.52,
     "importance": 0.13,
     "yolo": "bird",
     "yolo_conf": 0.62,
     "novel": false,
     "rejected": false,
     "constraints": "OK",
     "seg_status": "flag",
     "seg_note": "paths disagree: box says Living Being, segmentation says 'Static Object' (100% of object pixels)",
     "path": [
      {
       "name": "Object",
       "mass": 1.0,
       "floor": false
      },
      {
       "name": "Moving Object",
       "mass": 0.771,
       "floor": false
      },
      {
       "name": "Living Being",
       "mass": 0.523,
       "floor": true
      }
     ],
     "node_mass": {
      "Object": 1.0,
      "Moving Object": 0.771,
      "Living Being": 0.523,
      "Person": 0.156,
      "Pedestrian": 0.107,
      "Rider": 0.049,
      "Animal": 0.367,
      "Dog": 0.079,
      "Cat": 0.062,
      "Horse": 0.055,
      "Large Livestock": 0.058,
      "Bird": 0.113,
      "Vehicle": 0.249,
      "Two-Wheeler": 0.076,
      "Bicycle": 0.04,
      "Motorcycle": 0.035,
      "Road Vehicle": 0.147,
      "Passenger Car": 0.091,
      "Sedan": 0.04,
      "SUV": 0.051,
      "Commercial Vehicle": 0.057,
      "Transport Vehicle": 0.057,
      "Truck": 0.032,
      "Heavy Truck": 0.032,
      "MAN Truck": 0.032,
      "Bus": 0.025,
      "Rail Vehicle": 0.025,
      "Train": 0.025,
      "Static Object": 0.229,
      "Traffic Infrastructure": 0.139,
      "Traffic Light": 0.034,
      "Traffic Sign": 0.052,
      "Traffic Cone": 0.052,
      "Roadside Object": 0.089,
      "Bench": 0.026,
      "Fire Hydrant": 0.022,
      "Parking Meter": 0.042
     },
     "flat": {
      "leaf": "Bird",
      "prob": 0.11,
      "accepted": false
     }
    }
   ]
  }
 ]
};
