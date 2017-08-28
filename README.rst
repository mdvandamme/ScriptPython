# ScriptPython
Des scripts Python utilitaires



# Test - RST

L'objet principal du package est le *Solver* :

.. code-block:: java

   Solver solver = new Solver();

   
*Attention :* les expressions algébriques ne doivent contenir que des valeurs numériques (constantes) ou des paramètres 
à estimer (variables inconnues du problème). Le code ci-dessous est utilisé pour insérer des identificateurs 
Java dans l'expression des contraintes.


Le modèle de transformation utilisé est un modèle à 4 paramètres (Tx, Ty, k et ?). 
L'équation de changement de repère pour un point (x1,y1) s'écrit :

.. math::

    x2 = Tx + k*cos(?)*x1 + k*sin(?)*y1
    
    y2 = Ty - k*sin(?)*x1 + k*cos(?)*y1

On donne ci-dessous le code Java permettant de résoudre ce problème :

