# EXTREMELY LOW NOISE DATA ACQUISITION SYSTEM (DAQ)
<img width="3072" height="4080" alt="PXL_20260728_090040083(1)" src="https://github.com/user-attachments/assets/df5db7d0-14fa-415a-ba17-a47d2188022c" />
Measures mV level voltages and plots them on your computer screen, built using a raspberry pi pico and an OPA2134 op-amp signal conditioning stage, in order to plot REALLY accurate decay curves for an electromagnetic damping experiment with an active noise floor uncertainty of ±0.000034V!! <br/><br/>

> see this project in action: https://www.youtube.com/shorts/oiMqCiaboVs

I made this DAQ, because I was annoyed at the terrible analog oscilloscope in the lab, while trying to conduct an electromagnetic damping experiment. Since my lab didnt have a digital oscilloscope i could use, I thought "ill just make one myself". I did not realize at the time, just how deep this project would take me, and how obsessed i would become with analog signal conditioning. <br/>

# how to make your own!
<img width="3072" height="4080" alt="PXL_20260728_084321615" src="https://github.com/user-attachments/assets/df9b7698-cc3d-46fa-b593-478274b963c9" />

a "working" version of this device is quite simple, making a great version of this device is a lot harder. <br/>

feeding a constant voltage to the DAQ, and getting a quantized result with many "steps" of variation is inevitable when noise reduction measures have not been taken. <br/>

Most of the noise reduction is built in to the hardware and code. Keep all the wires short, the decoupling capacitors close to the pins, and ensure that the USB cable used to power the rasberry pi pico has its +5v bus cut off, and is instead powered through an external battery or power adapter. <br/>

<img width="566" height="835" alt="Screenshot from 2026-08-20 10-46-59" src="https://github.com/user-attachments/assets/75c1febf-af37-46eb-966a-4b9a36e2072a" />

[DAQ_electric_damp.pdf](https://github.com/user-attachments/files/31250556/DAQ_electric_damp.pdf)



# electric damping apparatus
<img width="3072" height="4080" alt="PXL_20260728_084732719" src="https://github.com/user-attachments/assets/5c4755c1-0d4d-458a-b15f-2ad6f0ce0077" />

A neodymium magnet is attached to a spring. An aluminum claw is used to release the magnet from a constant position with an initial velocity of zero. The magnet oscillates about the coil of wire, which induces EMF, Subsequently measured using the oscilloscope.  

# Stats

### Fixed Hardware Specs
| Parameter | Specification |
| :--- | :--- |
| **ADC Bit Depth** | 12-bit (4,096 levels) |
| **Reference Voltage** | +3.3V DC |
| **Virtual Ground Bias** | +1.65V DC |
| **ADC Pin Step Resolution (LSB)** | 0.806 mV |

### Configurable Specs (35× Gain Reference Setup)
| Parameter | Specification (@ 35× Gain) | Formula for Any Gain ($A_v$) |
| :--- | :--- | :--- |
| **Hardware Gain ($A_v$)** | 35x | User-Configurable |
| **Input Voltage Ceiling** | ±47.14 mV (94.28 mVp-p) | $\pm 1.65\text{V} / A_v$ |
| **Effective Coil Resolution** | 0.023 mV (23.03 μV) | $0.806\text{mV} / A_v$ |
| **Active Noise Floor Uncertainty** | ±0.034 mV (±34 μV) | Measured noise floor |
| **Signal-to-Noise Ratio (SNR)** | ~62.84 dB | 20 * log10(Voltage Ceiling / Noise Floor) |

# BOM (Bill Of Materials)
|Item                   |Qty.|Price (USD)|Link                                                                                                                              |
|-----------------------------|----|----------|----------------------------------------------------------------------------------------------------------------------------------|
|Breadboard                   |1   |2.21       |https://www.aliexpress.com/item/1005005239798226.html                                                                             |
|Rasberry Pi Pico             |1   |3.64       |https://www.aliexpress.us/item/3256808762485175.html                                                                              |
|NMA0515sc                    |1   |12.69      |https://www.lcsc.com/product-detail/C7010270.html                                                                                 |
|OPA2134PA op-amp             |1   |7.25       |https://www.lcsc.com/product-detail/C1346118.html                                                                                 |
|USB type C cable             |1   |2.63       |https://www.aliexpress.us/item/3256809634860310.html                                                                              |
|9V power adapter             |1   |2.96       |https://www.aliexpress.us/item/3256807586812399.html                                                                              |
|SPDT push button             |1   |3.36       |https://www.lcsc.com/product-detail/C318869.html                                                                                  |
|LM7805 voltage regulator     |1   |0.23       |https://www.lcsc.com/product-detail/C36350857.html?                                                                               |
|Signal diode                 |1   |1.64       |https://www.aliexpress.us/item/2251832278935821.html                                                                              |
|104 ceramic capacitor        |1   |3.36       |https://www.aliexpress.us/item/3256806988809232.html                                                                              |
|220uf electrolytic capacitor |1   |0.45       |https://www.lcsc.com/product-detail/C233093.html                                                                                  |
|22uf electrolytic capacitor  |1   |0.44       |https://www.lcsc.com/product-detail/C235681.html                                                                                  |
|10uf electrolytic capacitor  |1   |0.74       |https://www.lcsc.com/product-detail/C235887.html                                                                                  |
|1M ohm resistor              |1   |0.99       |https://www.aliexpress.us/item/3256811581264023.html                                                                              |
|35k ohm resistor             |1   |0.99       |https://www.aliexpress.us/item/3256811581264023.html                                                                              |
|10k ohm resistor             |1   |0.99       |https://www.aliexpress.us/item/3256811581264023.html                                                                              |
|1k ohm resistor              |1   |0.99       |https://www.aliexpress.us/item/3256811581264023.html |

Total (USD): $42.57


# notes
Muino serial plotter was mostly used to display the information, it is available as a Visual Studio Code extension.
A custom serial plotter was also made for this project by Hardyesh Kumar. It includes an extra post signal conditioning step called a **butterworth** filter.


Made with ❤️ by Umer

