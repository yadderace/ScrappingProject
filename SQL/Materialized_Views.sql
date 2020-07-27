create materialized view mvwSetLimpio as
select codigoencabezado, 
	cast(idregistro as integer) idregistro, cast(fecha_creacion as date) fechacreacion,
	cast(fecharegistro as date) fecharegistro, cast(valido_hasta as date) validohasta,
	cast(latitud as float) latitud, cast(longitud as float) longitud, 
	cast (espacio_m2 as float) espacio_m2, cast(administracion as float) administracion, 
	cast (precio as float) precio, cast(amueblado::numeric::integer as boolean) amueblado,
	cast(parqueo::numeric::integer as boolean) parqueo, cast(estudio::numeric::integer as boolean) estudio,
	cast(banos::numeric as integer) as banos, cast(piso::numeric as integer) as piso, 
	cast(habitaciones::numeric as integer) as habitaciones, cast(favoritos::numeric as integer) as favoritos,
	cast(tipo::numeric as integer) tipoinmueble, cast(tipo_vendedor::numeric as integer) as tipovendedor,
	moneda, descripcion, linkpagina, titulo,
	partner_code as partnercode,
	user_id as userid
from (
	select * 
	from crosstab('
				  	select codigoencabezado, nombrecampo, valordata
					from limpiezadata
					where nombrecampo <> ''codigoencabezado''
					order by 1, 2') 
	as ctb(
		codigoencabezado bigint, administracion text, amueblado text,
		antiguedad text, banos text, descripcion text,
		espacio_m2 text, estudio text, favoritos text,
		fecha_creacion text, fecharegistro text, habitaciones text,
		idregistro text, latitud text, linkpagina text,
		longitud text, moneda text, parqueo text,
		partner_code text, piso text, precio text,
		tipo text, tipo_vendedor text, titulo text,
		user_id text, valido_hasta text
	)) as pivot;
