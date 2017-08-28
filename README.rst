# ScriptPython
Des scripts Python utilitaires



# Test - RST

L'objet principal du package est le *Solver* :

.. code-block:: java

   Solver solver = new Solver();

   
*Attention :* les expressions alg�briques ne doivent contenir que des valeurs num�riques (constantes) ou des param�tres 
� estimer (variables inconnues du probl�me). Le code ci-dessous est utilis� pour ins�rer des identificateurs 
Java dans l'expression des contraintes.


Le mod�le de transformation utilis� est un mod�le � 4 param�tres (Tx, Ty, k et ?). 
L'�quation de changement de rep�re pour un point (x1,y1) s'�crit :

.. math::

    x2 = Tx + k*cos(?)*x1 + k*sin(?)*y1
    
    y2 = Ty - k*sin(?)*x1 + k*cos(?)*y1

On donne ci-dessous le code Java permettant de r�soudre ce probl�me :

