# Pycrown-Shocott-Spring

Shocott Spring Area Analysis Using PyCrown

The Python code developed as part of this study is designed to facilitate the integration of Airborne Laser Scanning (ALS) data into biomass and carbon estimation processes within the Woodland Carbon Code (WCC) framework. The code enables users to analyze ALS data to detect individual trees and estimate their biomass and carbon content.

## Key Features of the Code:

- **Individual Tree Detection**: Based on the [PyCrown Python package](https://github.com/manaakiwhenua/pycrown) by Zörner et al., 2018.
  
- **Individual Tree Metrics**: The code employs an algorithm to identify individual trees from ALS data using metrics such as tree height, diameter at breast height (DBH), and crown diameter. Crown diameter estimation is based on methods proposed by Jucker et al. (2017).

- **Biomass Estimation**: The code applies two methodologies for estimating above-ground biomass (AGB). It incorporates allometric equations developed by Jucker et al. (2017), as well as equations used within the WCC methodology (Method E) (Jenkins et al., 2018).

- **Customizability and Scalability**: The code is designed to be fully customizable. It allows users to import higher-resolution ALS data or adjust parameters to improve the accuracy of tree detection and biomass estimation.

## Purpose

The aim of the developed Python code is to provide a significant step toward integrating advanced remote sensing technologies into carbon accounting frameworks. It serves as a practical tool for forest managers and researchers to enhance the accuracy of biomass and carbon estimations, contributing to more reliable carbon offset initiatives.

## References

- Jenkins, T.A., Mackie, E.D., Matthews, R.W., Miller, G., Randle, T.J. and White, M.E., 2018. FC Woodland Carbon Code: Carbon Assessment Protocol (v2.0). *Forestry Commission, Version 2 (05).*

- Jucker, T., Caspersen, J., Chave, J., Antin, C., Barbier, N., Bongers, F., Dalponte, M., van Ewijk, K.Y., Forrester, D.I., Haeni, M. and Higgins, S.I., 2017. Allometric equations for integrating remote sensing imagery into forest monitoring programmes. *Global Change Biology*, *23*(1), pp.177-190.