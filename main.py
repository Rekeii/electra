import streamlit as st
import base64
import schemdraw
import schemdraw.elements as elm
import random

def to_engineering_notation(value, unit=''):
    """
    Convert value to engineering notation string with specified units
    Formats according to requirements: no leading zero decimals (e.g. 500.00m not 0.5)
    """
    if value == 0:
        return f"0 {unit}"
    
    prefixes = {
        -9: 'n',
        -6: 'μ',
        -3: 'm',
        0: '',
        3: 'k',
        6: 'M',
        9: 'G'
    }
    
    exponent = 0
    abs_val = abs(value)
    
    # Find appropriate exponent
    if abs_val >= 1000:
        while abs_val >= 1000 and exponent < 9:
            abs_val /= 1000
            exponent += 3
    elif abs_val < 1:
        while abs_val < 1 and exponent > -9:
            abs_val *= 1000
            exponent -= 3
    
    prefix = prefixes.get(exponent, '')
    
    # Format with 2 decimal places if needed, but remove trailing .00
    formatted = f"{abs_val:.2f}".rstrip('0').rstrip('.')
    
    # Handle trailing .00 for values that are exactly integers
    if '.' in formatted and formatted.endswith('.'):
        formatted = formatted[:-1]
    
    # Handle negative values
    if value < 0:
        formatted = f"-{formatted}"
    
    return f"{formatted}{prefix}{unit}"



class CircuitDrawer:
    def __init__(self):
        self.circuit_functions = {
            'series_clipper': self.series_clipper,
            'series_biasclipper': self.series_biasclipper,
            'parallel_clipper': self.parallel_clipper,
            'parallel_biasclipper': self.parallel_biasclipper,
            'nobias_clamper': self.nobias_clamper,
            'bias_clamper': self.bias_clamper,
            'zener_diode1': self.zener_diode1,
            'zener_diode2': self.zener_diode2,
            'zener_diode3': self.zener_diode3
        }

    def draw_circuit(self, circuit_type, *args):
        if circuit_type in self.circuit_functions:
            return self.circuit_functions[circuit_type](*args)
        else:
            raise ValueError(f"Unknown circuit type: {circuit_type}")

    def series_clipper(self, vin_peak, diode_reversed):
        return self._draw_clipper(vin_peak, diode_reversed, None, None)

    def series_biasclipper(self, vin_peak, diode_reversed, vbias, vbias_reversed):
        return self._draw_clipper(vin_peak, diode_reversed, vbias, vbias_reversed)

    def parallel_clipper(self, vin_peak, diode_reversed):
        return self._draw_parallel_clipper(vin_peak, diode_reversed, None, None)

    def parallel_biasclipper(self, vin_peak, diode_reversed, vbias, vbias_reversed):
        return self._draw_parallel_clipper(vin_peak, diode_reversed, vbias, vbias_reversed)

    def nobias_clamper(self, vin_peak, diode_reversed):
        return self._draw_clamper(vin_peak, diode_reversed, None, None)

    def bias_clamper(self, vin_peak, diode_reversed, vbias, vbias_reversed):
        return self._draw_clamper(vin_peak, diode_reversed, vbias, vbias_reversed)

    def zener_diode1(self, vin_peak, diode_reversed):
        with schemdraw.Drawing(show=False) as d:
            d += elm.SourceV().up().label(f'Vin={vin_peak:.1f} V')
            r_value = random.uniform(0.220, 10.0)
            d += elm.Resistor().right().label(f'{r_value:.3f} kΩ', loc='top')
            
            vz = st.session_state.vz  # Get from session state
            if diode_reversed:
                d += elm.Zener(reverse=True).down().label(f'Vz={vz:.1f}V', loc='bot')
            else:
                d += elm.Zener().down().label(f'Vz={vz:.1f}V', loc='bot')
                
            d += elm.Line().left()
            return d.get_imagedata('svg'), r_value, diode_reversed
    
    def zener_diode2(self, vin_peak, diode_reversed):
        with schemdraw.Drawing(show=False) as d:
            d += elm.SourceV().up().label('Vs')
            r1_value = random.uniform(0.220, 10.0)
            d += elm.Resistor().right().label(f'{r1_value:.3f} kΩ', loc='top')
            
            vz = st.session_state.vz  # Get from session state
            if diode_reversed:
                d += elm.Zener(reverse=True).down().label(f'{vz:.1f}V', loc='bot').hold()
            else:
                d += elm.Zener().down().label(f'Vz={vz:.1f}V', loc='bot').hold()
            
            d += elm.Line().right()
            r2_value = random.uniform(0.220, 10.0)
            d += elm.Resistor().down().label(f'{r2_value:.3f} kΩ', loc='bottom')
            d += elm.Line().left()
            d += elm.Line().left()
            
            return d.get_imagedata('svg'), (r1_value, r2_value), diode_reversed
    
    def zener_diode3(self, vin_peak, diode_reversed):
        with schemdraw.Drawing(show=False) as d:
            d += elm.SourceV().up().label(f'Vin={vin_peak:.1f} V')
            r1_value = random.uniform(0.220, 1.500)
            d += elm.Resistor().right().label(f'{r1_value:.3f} kΩ', loc='top')
            
            vz = st.session_state.vz
            if diode_reversed:
                d += elm.Zener(reverse=True).down().hold().label(f'{vz:.1f} V', loc='bottom')
            else:
                d += elm.Zener().down().hold()
            
            d += elm.Line().right()
            d += elm.ResistorVar().down().label('Rv', loc='bottom').reverse()
            d += elm.Line().left()
            d += elm.Line().left()
            
            return d.get_imagedata('svg'), r1_value, diode_reversed
    


    def _draw_clipper(self, vin_peak, diode_reversed, vbias, vbias_reversed):
        with schemdraw.Drawing(show=False) as d:
            d += elm.SourceV().up().label(f'Vin={vin_peak:.1f} V')
            
            if vbias is not None:
                if vbias_reversed:
                    d += elm.Battery().right().label(f'{vbias:.1f} V', loc='bottom').reverse()
                else:
                    d += elm.Battery().right().label(f'{vbias:.1f} V', loc='bottom')
            
            if diode_reversed:
                d += elm.Diode(reverse=True).right()
            else:
                d += elm.Diode().right()
            d.push()
            d += elm.Line().dot(open=True)
            d += elm.Gap().label(('+', '$V_o$', '-')).down()
            d.pop()
            r_value = random.uniform(0.220, 10.0)
            d += elm.Resistor().down()
            d += elm.Line().dot(open=True).right().hold()
            d += elm.Line().left()
            
            if vbias is not None:
                d += elm.Line()
            
            if vbias is not None:
                return d.get_imagedata('svg'), r_value, diode_reversed, vbias, vbias_reversed
            return d.get_imagedata('svg'), r_value, diode_reversed

    def _draw_parallel_clipper(self, vin_peak, diode_reversed, vbias, vbias_reversed):
        with schemdraw.Drawing(show=False) as d:
            d += elm.SourceV().up().label(f'Vin={vin_peak:.1f} V')
            d += elm.Line().right()
            r_value = random.uniform(0.220, 10.0)
            d += elm.Resistor().label(f'R={r_value:.3f} kΩ')
            d.push()
            d += elm.Line().dot(open=True)
            if vbias is not None:
                d += elm.Gap().label(('+', '', '$V_o$')).down()
                d += elm.Gap().label(('-')).down()
            else:
                d += elm.Gap().label(('+', '$V_o$', '-')).down()
            d.pop()
            if diode_reversed:
                d += elm.Diode(reverse=True).down()
            else:
                d += elm.Diode().down()
            if vbias is not None:
                if vbias_reversed:
                    d += elm.Battery().label(f'{vbias:.1f} V', loc='bottom').reverse()
                else:
                    d += elm.Battery().label(f'{vbias:.1f} V', loc='bottom')
            d += elm.Line().dot(open=True).right().hold()
            d += elm.Line().left()
            d += elm.Line().left()
            if vbias is not None:
                d += elm.Line().up()
            
            if vbias is not None:
                return d.get_imagedata('svg'), r_value, diode_reversed, vbias, vbias_reversed
            return d.get_imagedata('svg'), r_value, diode_reversed

    def _draw_clamper(self, vin_peak, diode_reversed, vbias, vbias_reversed):
        with schemdraw.Drawing(show=False) as d:
            d += elm.SourceV().up().label(f'Vin={vin_peak:.1f} V')
            d += elm.Capacitor2().right()
            
            d.push()
            if diode_reversed:
                d += elm.Diode(reverse=True).down()
            else:
                d += elm.Diode().down()
            if vbias is not None:
                if vbias_reversed:
                    d += elm.Battery().label(f'{vbias:.1f} V', loc='bottom').reverse()
                else:
                    d += elm.Battery().label(f'{vbias:.1f} V', loc='bottom')
                
            d.pop()
            d += elm.Line().right()
            
            d.push()
            d += elm.Line().dot(open=True)
            if vbias is not None:
                d += elm.Gap().label(('+', '', '$V_o$')).down()
                d += elm.Gap().label(('-')).down()
            else:
                d += elm.Gap().label(('+', '$V_o$', '-')).down()
            d.pop()
            
            r_value = random.uniform(0.220, 10.0)
            d += elm.Resistor().down()
            if vbias is not None:
                d += elm.Line()
            d += elm.Line().dot(open=True).right().hold()
            
            d += elm.Line().left()
            d += elm.Line().left()
            if vbias is not None:
                d += elm.Line().up()
            if vbias is not None:
                return d.get_imagedata('svg'), r_value, diode_reversed, vbias, vbias_reversed
            return d.get_imagedata('svg'), r_value, diode_reversed
        

def calculate_correct_values(vin, diode_reversed, circuit_type='series_clipper', vbias=None, vbias_reversed=None, vin_peak=None, vz=None, iz_max=None, iz_min=None):
    """Calculate correct values based on diode orientation and Vin"""
    if circuit_type == 'series_clipper':
        if not diode_reversed:
            return (True, vin) if vin > 0 else (False, 0)
        else:
            return (False, 0) if vin > 0 else (True, vin) 
            
    elif circuit_type == 'series_biasclipper':
        if vbias is None or vbias_reversed is None:
            return False, 0
        
        # Forward Diode cases
        if not diode_reversed:
            if not vbias_reversed:  # Bias is FORWARD
                if vin > vbias:
                    return True, vin - vbias  
                else:
                    return False, 0           
            else:                   # Bias is REVERSE
                if vin > 0:
                    return True, vin          
                elif vin < -vbias:
                    return False, 0           
                else:
                    return True, vin + vbias  
        # Reversed Diode cases ----------
        else:
            if not vbias_reversed:  # Bias is FORWARD
                if vin > 0 and vbias > vin:
                    return True, -vbias + vin  
                elif vin < 0:
                    return True, -vbias + vin  
                elif vin == 0:
                    return True, -vbias    
                else:
                    return False, 0      
            else:                   # Bias is REVERSE
                if vin > 0:
                    return False, 0
                elif abs(vin) > vbias:
                    return True, vin + vbias  
                else:
                    return False, 0           
                
    elif circuit_type == 'parallel_clipper':
        if not diode_reversed: 
            if vin > 0:
                return True, 0
            else:
                return False, vin
        else:  # Diode is reversed
            if vin > 0:
                return False, vin
            else:
                return True, 0
    
    elif circuit_type == 'parallel_biasclipper':
        if vbias is None or vbias_reversed is None:
            return False, 0
        
        # Forward Diode cases ---------
        if not diode_reversed:
            if not vbias_reversed:  # Bias is FORWARD
                if vin > 0 and vin > vbias:
                    return True, vbias
                elif vin <= 0:
                    return False, vin
                else:
                    return False, 0           
            else:                   # Bias is REVERSE
                if vin >= 0:
                    return True, -vbias          
                elif vin < 0 and abs(vbias) > abs(vin):
                    return True, -vbias
                elif vin < 0 and not(abs(vbias) > abs(vin)):
                    return False, vin           
                else:
                    return False, 0 
        # Reversed Diode cases ----------
        else:
            if not vbias_reversed:   # Bias is FORWARD
                if vin <= 0:
                    return True, vbias
                elif vin > 0 and vbias > vin:
                    return True, vbias
                elif vin > 0 and vin > vbias:
                    return False, vin
                else: 
                    return False, 0      
            else:                     # Bias is REVERSE
                if vin >= 0:
                    return False, vin
                elif abs(vin) > vbias:
                    return True, -vbias
                elif vin < 0 and abs(vin) < vbias:
                    return False, -vin
                else:
                    return False, 0          
    
    elif circuit_type == 'nobias_clamper':
        if vin_peak is None:
            return False, 0
        
        # Forward Diode cases --------- 
        if not diode_reversed:
            if vin >= 0:
                return False, vin - vin_peak   
            elif vin < 0:
                return False, vin - vin_peak
            else:
                return False, 0
        # Reverse Diode cases --------- 
        else:
            if vin <= 0:
                return False, vin + vin_peak
            elif vin > 0:
                return False, vin + vin_peak
            else:
                return False, 0
    
    elif circuit_type == 'bias_clamper':
        if vin_peak is None:
            return False, 0
        
        # Forward Diode cases --------- 
        if not diode_reversed:
            if not vbias_reversed:   # Bias is FORWARD
                if vin >= 0:
                    return False, vin - (vin_peak - vbias)   
                elif vin < 0:
                    return False, vin - (vin_peak - vbias)
                else:
                    return False, 0
            else:                    # Bias is REVERSE
                if vin <= 0:
                    return False, vin - (vin_peak + vbias)   
                elif vin > 0:
                    return False, vin - (vin_peak + vbias)
                else:
                    return False, 0
        # Reverse Diode cases --------- 
        else:
            if not vbias_reversed:   # Bias is FORWARD
                if vin <= 0:
                    return False, vin + (vin_peak + vbias)   
                elif vin > 0:
                    return False, vin + (vin_peak + vbias)
                else:
                    return False, 0
            else:                    # Bias is REVERSE
                if vin <= 0:
                    return False, vin + (vin_peak - vbias)   
                elif vin > 0:
                    return False, vin + (vin_peak - vbias)
                else:
                    return False, 0
    
    elif circuit_type == 'zener_diode1':
        if vin_peak is None or vz is None:
            return False, 0, 0, 0, 0
        r_value = st.session_state.r_value*1000
        Vr = vin_peak - vz
        Ir = Vr / r_value
        Pr = Ir * Vr
        Pz = Ir * vz
        return True, Vr, Ir, Pr, Pz

    elif circuit_type == 'zener_diode2':
        if vin_peak is None or vz is None:
            return False, 0, 0, 0, 0, 0, 0, 0
        r_values = st.session_state.r_value*1000
        Il = vz / r_values[1]
        if iz_min: #if iz_max exists (iz min is either 0 or a random number)
            Ir_min = iz_min + Il
        else:
            Ir_max = iz_max + Il
            Ir_min = Il
            iz_min = 0
        Vr_max = iz_max * r_values[0]  # Use r1_value
        Vs_max = Vr_max + vz
        Vr_min = iz_min * r_values[0]   # Use r1_value
        Vs_min = Vr_min + vz
        return True, Il, Vr_max, Vs_max, Vr_min, Vs_min, 0, 0

    elif circuit_type == 'zener_diode3':
        if vin_peak is None or vz is None:
            return False, 0, 0, 0, 0, 0, 0, 0
        r_value = st.session_state.r_value * 1000
        Vr = vin_peak - vz
        Ir = Vr / r_value
        Il_max = Ir - iz_max 
        if iz_min is not None:
            Il_min = Ir - iz_min 
        else:
            Il_min = Ir
            iz_min = 0
        Rl_max = vz / Il_max if Il_max != 0 else float('inf')
        Rl_min = vz / Il_min if Il_min != 0 else float('inf')
        return True, Vr, Ir, Il_max, Il_min, Rl_max, Rl_min, 0, 0, 0

    
    return False, 0, 0, 0, 0

        

def setup_circuit(drawer, circuit_type):
    diode_reversed = True  # Force reverse bias for Zener diodes
    if circuit_type == 'zener_diode3':
        vin_peak = round(random.uniform(20.0, 75.0), 1)
    else:
        vin_peak = round(random.uniform(5.0, 20.0), 1)
    
    if circuit_type in ['series_clipper', 'parallel_clipper', 'nobias_clamper']:
        diode_reversed = random.choice([True, False])
        result = drawer.draw_circuit(circuit_type, vin_peak, diode_reversed)
        return (*result[:3], vin_peak, None, None)
    
    elif circuit_type in ['series_biasclipper', 'parallel_biasclipper', 'bias_clamper']:
        diode_reversed = random.choice([True, False])
        vbias = random.uniform(2.0, 10.0)
        vbias_reversed = random.choice([True, False])
        result = drawer.draw_circuit(circuit_type, vin_peak, diode_reversed, vbias, vbias_reversed)
        return (*result, vin_peak)
    
    elif circuit_type in ['zener_diode1', 'zener_diode2']:
        # Generate Zener parameters first
        if random.random() < 0.8:  # 80% of the time
            vz = round(random.uniform(vin_peak * 0.2, vin_peak * 0.8), 1)
        else:
            vz = round(random.uniform(vin_peak * 0.8, vin_peak * 1.2), 1)
        
        iz_max = random.uniform(5.0, 30.0)
        iz_min = random.uniform(1.0, iz_max * 0.2) if random.random() < 0.2 else None  # 20% of the time
        
        # Store in session state before drawing
        st.session_state.vz = vz
        st.session_state.iz_max = iz_max
        st.session_state.iz_min = iz_min
        
        # Now draw the circuit
        result = drawer.draw_circuit(circuit_type, vin_peak, True)  # Remove vz parameter
        
        if circuit_type == 'zener_diode1':
            return (*result, vin_peak, None, None, vz, iz_max, iz_min)
        else:
            return (*result, vin_peak, None, None, vz, iz_max, iz_min)
    
    elif circuit_type == 'zener_diode3':
        # Generate Zener parameters first
        if random.random() < 0.8:  # 80% of the time
            vz = round(random.uniform(vin_peak * 0.2, vin_peak * 0.8), 1)
        else:
            vz = round(random.uniform(vin_peak * 0.8, vin_peak * 1.2), 1)
        
        iz_max = random.uniform(2.0, 25.0)
        iz_min = random.uniform(1.0, iz_max * 0.2) if random.random() < 0.2 else None  # 20% of the time
        
        # Store in session state before drawing
        st.session_state.vz = vz
        st.session_state.iz_max = iz_max
        st.session_state.iz_min = iz_min
        
        # Now draw the circuit
        result = drawer.draw_circuit(circuit_type, vin_peak, True)  # Remove vz parameter
        return (*result, vin_peak, None, None, vz, iz_max, iz_min)
    
    return None, None, None, None, None, None, None, None, None




def display_circuit(svg_image, r_value, diode_reversed, vbias=None, vbias_reversed=None, vz=None, iz_max=None, iz_min=None):
    if svg_image:
        st.markdown(
            f'<img src="data:image/svg+xml;base64,{base64.b64encode(svg_image).decode()}" />',
            unsafe_allow_html=True
        )
        
        if isinstance(r_value, tuple):
            st.write(f"Resistors: R1={to_engineering_notation(r_value[0]*1000, 'Ω')}, R2={to_engineering_notation(r_value[1]*1000, 'Ω')}")
        else:
            st.write(f"Resistor: {to_engineering_notation(r_value*1000, 'Ω')}")

        st.write(f"Diode: {'Reverse' if diode_reversed else 'Forward'} biased")
        
        # Fixed order of parameters and added proper engineering notation
        if vz is not None:
            st.write(f"Zener Voltage (Vz): {to_engineering_notation(vz, 'V')}")
            
        if iz_max is not None:
            st.write(f"Zener Max Current (Iz_max): {to_engineering_notation(iz_max, 'A')}")
            
        if iz_min is not None:
            st.write(f"Zener Min Current (Iz_min): {to_engineering_notation(iz_min, 'A')}")
        elif iz_min is None:
            st.write("Zener Min Current (Iz_min): N/A")
            
        if vbias is not None:
            st.write(f"Bias: {to_engineering_notation(vbias, 'V')} ({'Reversed' if vbias_reversed else 'Forward'})")
            
        st.divider()





def display_form(vin_peak, diode_reversed, circuit_type='series_clipper', vbias=None, vbias_reversed=None):
    with st.form(key='input_form'):
        if circuit_type in ['nobias_clamper', 'bias_clamper']:
            # Simplified form for clamper circuits (no D column needed)
            cols = st.columns([1, 1])
            cols[0].markdown("<div style='text-align: center'><b>Vin (V)</b></div>", unsafe_allow_html=True)
            cols[1].markdown("<div style='text-align: center'><b>Vo (V)</b></div>", unsafe_allow_html=True)
            
            data = [vin_peak, vin_peak - 2.5, 0, -(vin_peak - 2.5), -vin_peak]
            table_data = []
            
            for vin in data:
                with st.container():
                    cols = st.columns([1, 1])
                    
                    # Vin value
                    with cols[0]:
                        st.markdown(
                            f"<div style='display: flex; align-items: center; height: 100%'>"
                            f"<div style='width: 100%; text-align: center; padding-top:20px'>{vin:.1f}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    
                    # Number input
                    with cols[1]:
                        st.markdown(
                            "<div style='display: flex; justify-content: center; align-items: center; height: 100%'>",
                            unsafe_allow_html=True
                        )
                        vout_input = st.number_input(
                            "Vout", 
                            key=f"vout_{vin}_{circuit_type}", 
                            label_visibility="collapsed",
                            step=0.1,
                            format="%.1f"
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    table_data.append([vin, vout_input])
            
            if st.form_submit_button("Check"):
                results = []
                for vin, user_vout in table_data:
                    correct_fb, correct_vout = calculate_correct_values(
                        vin, diode_reversed, circuit_type, vbias, vbias_reversed, vin_peak
                    )
                    is_correct = abs(float(user_vout) - correct_vout) < 0.1
                    results.append({
                        "Vin": vin,
                        "Your Vout": user_vout,
                        "Correct Vout": correct_vout,
                        "Is Correct": is_correct
                    })
                return results

        elif circuit_type == 'zener_diode1':
            # Custom form for zener_diode1
            st.subheader("Zener Diode (Basic) Parameters")
            I = st.number_input("Current (I)", min_value=0.0, step=0.1)
            Pr = st.number_input("Power across Resistor (Pr)", min_value=0.0, step=0.1)
            Pz = st.number_input("Power across Zener (Pz)", min_value=0.0, step=0.1)
            Vr = st.number_input("Voltage across Resistor (Vr)", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Check"):
                correct_values = calculate_correct_values(
                    vin_peak, diode_reversed, circuit_type, 
                    vin_peak=vin_peak, 
                    vz=st.session_state.vz,
                    iz_max=st.session_state.iz_max,
                    iz_min=st.session_state.iz_min
                )
                results = [{
                    "ZenerDiode1": {
                        "Vr": Vr,
                        "Ir": I,
                        "Pr": Pr,
                        "Pz": Pz,
                        "Iz_max": st.session_state.iz_max,
                        "Iz_min": st.session_state.iz_min,
                        "Correct Vr": correct_values[1],
                        "Correct Ir": correct_values[2],
                        "Correct Pr": correct_values[3],
                        "Correct Pz": correct_values[4]
                    }
                }]
                return results

        elif circuit_type == 'zener_diode2':
            # Custom form for zener_diode2
            st.subheader("Zener Diode (Two Resistors) Parameters")
            
            st.markdown("**General Parameters**")
            Il = st.number_input("Load Current (Il)", min_value=0.0, step=0.1)
            Iz_max = st.number_input("Zener Max Current (Iz(max))", min_value=0.0, step=0.1)
            Iz_min = st.number_input("Zener Min Current (Iz(min))", min_value=0.0, step=0.1)
            
            st.markdown("**At Iz(max)**")
            col1, col2 = st.columns(2)
            with col1:
                Vr_max = st.number_input("Vr at Iz(max)", min_value=0.0, step=0.1)
            with col2:
                Vs_max = st.number_input("Vs at Iz(max)", min_value=0.0, step=0.1)
            
            st.markdown("**At Iz(min)**")
            col1, col2 = st.columns(2)
            with col1:
                Vr_min = st.number_input("Vr at Iz(min)", min_value=0.0, step=0.1)
            with col2:
                Vs_min = st.number_input("Vs at Iz(min)", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Check"):
                correct_values = calculate_correct_values(
                    vin_peak, diode_reversed, circuit_type, 
                    vin_peak=vin_peak, 
                    vz=st.session_state.vz,
                    iz_max=st.session_state.iz_max,
                    iz_min=st.session_state.iz_min,
                )
                results = [{
                    "ZenerDiode2": {
                        "Vr_max": Vr_max,
                        "Vs_max": Vs_max,
                        "Vr_min": Vr_min,
                        "Vs_min": Vs_min,
                        "Iz_max": st.session_state.iz_max,
                        "Iz_min": st.session_state.iz_min,
                        "Il": Il,
                        "Correct Il": correct_values[1],
                        "Correct Vr_max": correct_values[2],
                        "Correct Vs_max": correct_values[3],
                        "Correct Vr_min": correct_values[4],
                        "Correct Vs_min": correct_values[5],
                    }
                }]  
                return results
            

        elif circuit_type == 'zener_diode3':
            # Custom form for zener_diode3
            st.subheader("Zener Diode (Variable Resistor) Parameters")
            
            st.markdown("**General Parameters**")
            Vr = st.number_input("Voltage across Resistor (Vr)", min_value=0.0, step=0.1)
            Ir = st.number_input("Current through Resistor (Ir)", min_value=0.0, step=0.1)
            Iz_max = st.number_input("Zener Max Current (Iz(max))", min_value=0.0, step=0.1)
            Iz_min = st.number_input("Zener Min Current (Iz(min))", min_value=0.0, step=0.1)
            
            st.markdown("**At Iz(max)**")
            col1, col2 = st.columns(2)
            with col1:
                Il_max = st.number_input("Load Current at Iz(max)", min_value=0.0, step=0.1)
            with col2:
                Rl_max = st.number_input("Load Resistance at Iz(max)", min_value=0.0, step=0.1)
            
            st.markdown("**At Iz(min)**")
            col1, col2 = st.columns(2)
            with col1:
                Il_min = st.number_input("Load Current at Iz(min)", min_value=0.0, step=0.1)
            with col2:
                Rl_min = st.number_input("Load Resistance at Iz(min)", min_value=0.0, step=0.1)
            
            if st.form_submit_button("Check"):
                correct_values = calculate_correct_values(
                    vin_peak, diode_reversed, circuit_type, 
                    vin_peak=vin_peak, 
                    vz=st.session_state.vz,
                    iz_max=st.session_state.iz_max,
                    iz_min=st.session_state.iz_min
                )
                results = [{
                    "ZenerDiode3": {
                        "Vr": Vr,
                        "Ir": Ir,
                        "Rl_max": Rl_max,
                        "Rl_min": Rl_min,
                        "Iz_max": st.session_state.iz_max,
                        "Iz_min": st.session_state.iz_min,
                        "Il_max": Il_max,  # From form inputs
                        "Il_min": Il_min,  # From form inputs
                        "Correct Vr": correct_values[1],
                        "Correct Ir": correct_values[2],
                        "Correct Il_max": correct_values[3],
                        "Correct Il_min": correct_values[4],
                        "Correct Rl_max": correct_values[5],
                        "Correct Rl_min": correct_values[6]
                    }
                }]



                return results



        else:
            # Default form for clipper circuits
            cols = st.columns([1, 1, 2])
            cols[0].markdown("<div style='text-align: center'><b>Vin (V)</b></div>", unsafe_allow_html=True)
            cols[1].markdown("<div style='text-align: center'><b>D</b></div>", unsafe_allow_html=True)
            cols[2].markdown("<div style='text-align: center'><b>Vo (V)</b></div>", unsafe_allow_html=True)
            
            data = [vin_peak, vin_peak - 2.5, 0, -(vin_peak - 2.5), -vin_peak]
            table_data = []
            
            for vin in data:
                with st.container():
                    cols = st.columns([1, 1, 2])
                    
                    # Vin value
                    with cols[0]:
                        st.markdown(
                            f"<div style='display: flex; align-items: center; height: 100%'>"
                            f"<div style='width: 100%; text-align: center; padding-top:20px'>{vin:.1f}</div>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    
                    # Checkbox
                    with cols[1]:
                        st.markdown(
                            "<div style='display: flex; justify-content: center; align-items: center; height: 100%'>",
                            unsafe_allow_html=True
                        )
                        fb_checkbox = st.checkbox("FB", key=f"fb_{vin}_{circuit_type}", label_visibility="collapsed")
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Number input
                    with cols[2]:
                        st.markdown(
                            "<div style='display: flex; justify-content: center; align-items: center; height: 100%'>",
                            unsafe_allow_html=True
                        )
                        vout_input = st.number_input(
                            "Vout", 
                            key=f"vout_{vin}_{circuit_type}", 
                            label_visibility="collapsed",
                            step=0.1,
                            format="%.1f"
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    table_data.append([vin, fb_checkbox, vout_input])
            
            if st.form_submit_button("Check"):
                results = []
                for vin, user_fb, user_vout in table_data:
                    correct_fb, correct_vout = calculate_correct_values(
                        vin, diode_reversed, circuit_type, vbias, vbias_reversed, vin_peak
                    )
                    is_correct = (abs(float(user_vout) - correct_vout) < 0.1) and (user_fb == correct_fb)
                    results.append({
                        "Vin": vin,
                        "Your FB": "FB" if user_fb else "RB",
                        "Correct FB": "FB" if correct_fb else "RB",
                        "Your Vout": user_vout,
                        "Correct Vout": correct_vout,
                        "Is Correct": is_correct
                    })
                return results
    
    return None



def display_results(results):
    if not results:
        return
    
    if isinstance(results[0], dict) and "ZenerDiode1" in results[0]:
        st.subheader("Zener Diode (Basic) Results")
        result = results[0]["ZenerDiode1"]
        cols = st.columns(2)
        with cols[0]:
            st.write(f"Vr: {to_engineering_notation(result['Vr'], 'V')} (Correct: {to_engineering_notation(result['Correct Vr'], 'V')})")
            st.write(f"Ir: {to_engineering_notation(result['Ir'], 'A')} (Correct: {to_engineering_notation(result['Correct Ir'], 'A')})")
        with cols[1]:
            st.write(f"Iz_max: {to_engineering_notation(result['Iz_max'], 'A')}")
            st.write(f"Iz_min: {to_engineering_notation(result['Iz_min'], 'A') if result['Iz_min'] is not None else 'N/A'}")
        st.write(f"Pr: {to_engineering_notation(result['Pr'], 'W')} (Correct: {to_engineering_notation(result['Correct Pr'], 'W')})")
        st.write(f"Pz: {to_engineering_notation(result['Pz'], 'W')} (Correct: {to_engineering_notation(result['Correct Pz'], 'W')})")
    
    elif isinstance(results[0], dict) and "ZenerDiode2" in results[0]:
        st.subheader("Zener Diode (Two Resistors) Results")
        result = results[0]["ZenerDiode2"]
        cols = st.columns(2)
        with cols[0]:
            st.write(f"Vr_max: {to_engineering_notation(result['Vr_max'], 'V')} (Correct: {to_engineering_notation(result['Correct Vr_max'], 'V')})")
            st.write(f"Vs_max: {to_engineering_notation(result['Vs_max'], 'V')} (Correct: {to_engineering_notation(result['Correct Vs_max'], 'V')})")
            st.write(f"Iz_max: {to_engineering_notation(result['Iz_max'], 'A')}") 
            st.write(f"Il: {to_engineering_notation(result['Il'], 'A')} (Correct: {to_engineering_notation(result['Correct Il'], 'A')})")
        with cols[1]:
            st.write(f"Vr_min: {to_engineering_notation(result['Vr_min'], 'V')} (Correct: {to_engineering_notation(result['Correct Vr_min'], 'V')})")
            st.write(f"Vs_min: {to_engineering_notation(result['Vs_min'], 'V')} (Correct: {to_engineering_notation(result['Correct Vs_min'], 'V')})")
            st.write(f"Iz_min: {to_engineering_notation(result['Iz_min'], 'A') if result['Iz_min'] is not None else 'N/A'}")
    
    elif isinstance(results[0], dict) and "ZenerDiode3" in results[0]:
        st.subheader("Zener Diode (Variable Resistor) Results")
        result = results[0]["ZenerDiode3"]
        cols = st.columns(2)
        with cols[0]:
            st.write(f"Vr: {to_engineering_notation(result['Vr'], 'V')} (Correct: {to_engineering_notation(result['Correct Vr'], 'V')})")
            st.write(f"Ir: {to_engineering_notation(result['Ir'], 'A')} (Correct: {to_engineering_notation(result['Correct Ir'], 'A')})")
        with cols[1]:
            st.write(f"Il_max: {to_engineering_notation(result['Il_max'], 'A')} (Correct: {to_engineering_notation(result['Correct Il_max'], 'A')})")
            st.write(f"Il_min: {to_engineering_notation(result['Il_min'], 'A') if result['Il_min'] is not None else 'N/A'} (Correct: {to_engineering_notation(result['Correct Il_min'], 'A')})")
        st.write(f"Rl_max: {to_engineering_notation(result['Rl_max'], 'Ω')} (Correct: {to_engineering_notation(result['Correct Rl_max'], 'Ω')})")
        st.write(f"Rl_min: {to_engineering_notation(result['Rl_min'], 'Ω')} (Correct: {to_engineering_notation(result['Correct Rl_min'], 'Ω')})")

        
    elif "Your FB" in results[0]:  # For clipper circuits
        st.subheader("Results")
        for result in results:
            fb_color = "green" if result["Your FB"] == result["Correct FB"] else "red"
            vout_color = "green" if abs(float(result["Your Vout"]) - result["Correct Vout"]) < 0.1 else "red"
            st.markdown(
                f"Vin = {result['Vin']:.1f}V | "
                f"Your FB: <span style='color:{fb_color}'>{result['Your FB']}</span> | "
                f"Correct FB: {result['Correct FB']} | "
                f"Your Vout: <span style='color:{vout_color}'>{result['Your Vout']}</span> | "
                f"Correct Vout: {result['Correct Vout']:.1f}",
                unsafe_allow_html=True
            )
    else:  # For clamper circuits
        st.subheader("Results")
        for result in results:
            vout_color = "green" if abs(float(result["Your Vout"]) - result["Correct Vout"]) < 0.1 else "red"
            st.markdown(
                f"Vin = {result['Vin']:.1f}V | "
                f"Your Vout: <span style='color:{vout_color}'>{result['Your Vout']}</span> | "
                f"Correct Vout: {result['Correct Vout']:.1f}",
                unsafe_allow_html=True
            )

def main():
    drawer = CircuitDrawer()
    
    if 'svg_image' not in st.session_state:
        st.session_state.update({
            'svg_image': None,
            'r_value': None,
            'diode_reversed': None,
            'vin_peak': random.uniform(5.0, 20.0),
            'vbias': None,
            'vbias_reversed': None,
            'vz': None,
            'iz_max': None,
            'iz_min': None,
            'show_results': False,
            'results': None,
            'circuit_type': None
        })

    colMain, colNav = st.columns([3, 1])
    
    with colMain:
        st.title("Electra")
        st.divider()
        
        st.info('Disregard Iz_max if Zener Diode (Basic)', icon="ℹ️")
        
        if st.session_state.svg_image:
            display_circuit(
                st.session_state.svg_image, 
                st.session_state.r_value, 
                st.session_state.diode_reversed,
                st.session_state.vbias,
                st.session_state.vbias_reversed,
                st.session_state.vz,
                st.session_state.iz_max,
                st.session_state.iz_min
            )
            
            results = display_form(
                st.session_state.vin_peak, 
                st.session_state.diode_reversed, 
                st.session_state.circuit_type,
                st.session_state.vbias,
                st.session_state.vbias_reversed
            )

            if results:
                st.session_state.results = results
                st.session_state.show_results = True
                st.rerun()
                
            if st.session_state.show_results and st.session_state.results:
                display_results(st.session_state.results)

    with colNav:
        # CLIPPER CIRCUIT -------------
        if st.button('Series Clipper'):
            svg_image, r_value, diode_reversed, vin_peak, _, _ = setup_circuit(drawer, 'series_clipper')
            if svg_image:
                st.session_state.svg_image = svg_image
                st.session_state.r_value = r_value
                st.session_state.diode_reversed = diode_reversed
                st.session_state.vin_peak = vin_peak
                st.session_state.vbias = None
                st.session_state.vbias_reversed = None
                st.session_state.circuit_type = 'series_clipper'
                st.session_state.show_results = False
                st.session_state.results = None
                st.rerun()

        if st.button('Series Bias Clipper'):
            svg_image, r_value, diode_reversed, vin_peak, vbias, vbias_reversed = setup_circuit(drawer, 'series_biasclipper')
            if svg_image:
                st.session_state.svg_image = svg_image
                st.session_state.r_value = r_value
                st.session_state.diode_reversed = diode_reversed
                st.session_state.vin_peak = vin_peak
                st.session_state.vbias = vbias
                st.session_state.vbias_reversed = vbias_reversed
                st.session_state.circuit_type = 'series_biasclipper'
                st.session_state.show_results = False
                st.session_state.results = None
                st.rerun()

        if st.button('Parallel Clipper'):
            svg_image, r_value, diode_reversed, vin_peak, _, _ = setup_circuit(drawer, 'parallel_clipper')
            if svg_image:
                st.session_state.svg_image = svg_image
                st.session_state.r_value = r_value
                st.session_state.diode_reversed = diode_reversed
                st.session_state.vin_peak = vin_peak
                st.session_state.vbias = None
                st.session_state.vbias_reversed = None
                st.session_state.circuit_type = 'parallel_clipper'
                st.session_state.show_results = False
                st.session_state.results = None
                st.rerun()
                
        if st.button('Parallel Bias Clipper'):
            svg_image, r_value, diode_reversed, vin_peak, vbias, vbias_reversed = setup_circuit(drawer, 'parallel_biasclipper')
            if svg_image:
                st.session_state.svg_image = svg_image
                st.session_state.r_value = r_value
                st.session_state.diode_reversed = diode_reversed
                st.session_state.vin_peak = vin_peak
                st.session_state.vbias = vbias
                st.session_state.vbias_reversed = vbias_reversed
                st.session_state.circuit_type = 'parallel_biasclipper'
                st.session_state.show_results = False
                st.session_state.results = None
                st.rerun()
        
        st.divider()
        
        # CLAMPER CIRCUIT -------------
        
        if st.button('No Bias Clamper'):
            svg_image, r_value, diode_reversed, vin_peak, _, _ = setup_circuit(drawer, 'nobias_clamper')
            if svg_image:
                st.session_state.svg_image = svg_image
                st.session_state.r_value = r_value
                st.session_state.diode_reversed = diode_reversed
                st.session_state.vin_peak = vin_peak
                st.session_state.vbias = None
                st.session_state.vbias_reversed = None
                st.session_state.circuit_type = 'nobias_clamper'
                st.session_state.show_results = False
                st.session_state.results = None
                st.rerun()
        
        if st.button('Bias Clamper'):
            svg_image, r_value, diode_reversed, vin_peak, vbias, vbias_reversed = setup_circuit(drawer, 'bias_clamper')
            if svg_image:
                st.session_state.svg_image = svg_image
                st.session_state.r_value = r_value
                st.session_state.diode_reversed = diode_reversed
                st.session_state.vin_peak = vin_peak
                st.session_state.vbias = vbias
                st.session_state.vbias_reversed = vbias_reversed
                st.session_state.circuit_type = 'bias_clamper'
                st.session_state.show_results = False
                st.session_state.results = None
                st.rerun()       
        
        st.divider()
        if st.button('Zener Diode (Basic)'):
            setup_result = setup_circuit(drawer, 'zener_diode1')
            if setup_result[0]:
                svg_image, r_value, diode_reversed, vin_peak, _, _, vz, iz_max, iz_min = setup_result
                st.session_state.update({
                    'svg_image': svg_image,
                    'r_value': r_value,
                    'diode_reversed': diode_reversed,
                    'vin_peak': vin_peak,
                    'vz': vz,  # Ensure vz is stored
                    'iz_max': iz_max,
                    'iz_min': iz_min,
                    'circuit_type': 'zener_diode1',
                    'show_results': False,
                    'results': None
                })
                st.rerun()

        if st.button('Zener Diode (Two Resistors)'):
            setup_result = setup_circuit(drawer, 'zener_diode2')
            if setup_result[0]:  # Check if svg_image exists
                svg_image, r_values, diode_reversed, vin_peak, _, _, vz, iz_max, iz_min = setup_result
                st.session_state.update({
                    'svg_image': svg_image,
                    'r_value': r_values,
                    'diode_reversed': diode_reversed,
                    'vin_peak': vin_peak,
                    'vbias': None,
                    'vbias_reversed': None,
                    'vz': vz,
                    'iz_max': iz_max,
                    'iz_min': iz_min,
                    'circuit_type': 'zener_diode2',
                    'show_results': False,
                    'results': None
                })
                st.rerun()

        if st.button('Zener Diode (Variable Resistor)'):
            setup_result = setup_circuit(drawer, 'zener_diode3')
            if setup_result[0]:  # Check if svg_image exists
                svg_image, r_value, diode_reversed, vin_peak, _, _, vz, iz_max, iz_min = setup_result
                st.session_state.update({
                    'svg_image': svg_image,
                    'r_value': r_value,
                    'diode_reversed': diode_reversed,
                    'vin_peak': vin_peak,
                    'vbias': None,
                    'vbias_reversed': None,
                    'vz': vz,
                    'iz_max': iz_max,
                    'iz_min': iz_min,
                    'circuit_type': 'zener_diode3',
                    'show_results': False,
                    'results': None
                })
                st.rerun()

if __name__ == "__main__":
    main()
