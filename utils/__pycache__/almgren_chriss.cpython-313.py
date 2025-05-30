�
    z�%h�  �                   �,   � S SK rS rS rSS jrSS jrg)�    Nc                 �   � X U-  -  $ )z/
Temporary impact function: eta * volume^alpha
� )�volume�alpha�etas      �RC:\Users\VICTUS\Downloads\goquant-trade-simulator-complete\utils\almgren_chriss.py�temporary_impactr	      s   � � �5�� � �    c                 �   � X U-  -  $ )z0
Permanent impact function: gamma * volume^beta
r   )r   �beta�gammas      r   �permanent_impactr   	   s   � � �T�>�!�!r
   c	                 �   � X!-  [        X-  XE5      -  n	X U-
  -  U-  [        X-  X65      -  n
SUS-  -  US-  -  U-  X-
  S-  -  nX�-   U-   $ )zq
Hamiltonian function (objective to minimize):
Considers permanent impact, temporary impact, and execution risk.
�      �?�   )r   r	   )�	inventory�sell_amount�risk_aversionr   r   r   r   �
volatility�	time_step�temp_impact�perm_impact�	exec_risks               r   �hamiltonianr      sz   � �
  �-�0@��AX�Z^�0f�f�K��{�#:�;�i�G�JZ�[f�[r�ty�J��K��}��)�*�j�A�o�>��J�y�Of�kl�Nl�m�I��$�y�0�0r
   c                 �&  � [         R                  " XS-   4SS9n[         R                  " XS-   4SS9n	[         R                  " U S4SS9n
XS'   / nSnS n[        US-   5       H,  nU[        X�-  X65      -  nU" U5      X�S-
  U4'   X�U S-
  U4'   M.     [        U S-
  S	S	5       H�  n[        US-   5       Hu  nUUS-   S4   U" [	        X�X#XEXgU5	      5      -  nUn[        U5       H3  nUUS-   UU-
  4   U" [	        UUX#XEXgU5	      5      -  nUU:  d  M/  UnUnM5     UUUU4'   UU	UU4'   Mw     M�     [        SU 5       H8  nU
US-
     U	UU
US-
     4   -
  U
U'   UR                  U	UU
US-
     4   5        M:     [         R                  " U5      nX�X�4$ )
aR  
Computes the optimal trading trajectory using dynamic programming based on the Almgren-Chriss model.

Parameters:
- time_steps: Number of time intervals
- total_shares: Total number of shares to be liquidated
- risk_aversion: Risk aversion parameter
- alpha, beta: Exponents for temporary and permanent market impact
- gamma, eta: Coefficients for permanent and temporary market impact
- volatility: Market volatility

Returns:
- value_function: Cost matrix
- best_moves: Best action at each state
- inventory_path: Remaining shares over time
- optimal_trajectory: Optimal share sell sequence
�   �float64)�dtype�intr   r   c                 �Z   � [         R                  " [         R                  " U SS5      5      $ )NiD���i�  )�np�exp�clip)�xs    r   �safe_exp�#optimal_execution.<locals>.safe_exp4   s   � ��v�v�b�g�g�a��s�+�,�,r
   r   �����)r!   �zeros�ranger	   r   �append�asarray)�
time_steps�total_sharesr   r   r   r   r   r   �value_function�
best_moves�inventory_path�optimal_trajectory�time_step_sizer%   �shares�val�t�
best_value�best_share_amount�n�current_values                        r   �optimal_executionr:      s  � �& �X�X�z�!�+;�<�I�N�N����:�a�'7�8��F�J��X�X�z�1�o�U�;�N�$�1�����N�-�
 ��q�(�)���'��(?��L�L��19�#���A�~�v�-�.�-3�:��>�6�)�*� *� �:��>�2�r�*���L�1�,�-�F�'��A��q��1�H��F�M�$�s�`n�o�5� �J� !'���6�]�� .�q�1�u�f�q�j�/@� A�H����=��c�_m�n�E� !�� !�:�-�!.�J�()�%� #� )3�N�1�f�9�%�$5�J�q�&�y�!� .� +�" �1�j�!��*�1�q�5�1�J�q�.�QR�UV�QV�BW�?W�4X�X��q���!�!�*�Q��q�1�u�0E�-E�"F�G� "� ���$6�7���~�I�Ir
   )�333333�?r   )r;   )�numpyr!   r	   r   r   r:   r   r
   r   �<module>r=      s   �� �!�"�1�=Jr
   